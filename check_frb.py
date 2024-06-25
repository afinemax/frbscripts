#!/usr/bin/env python3

from argparse import ArgumentParser
import subprocess
import os
from glob import glob
from your.formats.pysigproc import SigprocFile
from datetime import datetime
from tqdm import tqdm
from candidate_maker import make_candidates_for_singlepulsefile

# ignore chan filenames 
# should be located in same dir as this script
p_ignore = 'p_band_master.ignorechans'
l1_ignore = 'l1_band_master.ignorechans'
l2_ignore = 'l2_band_master.ignorechans'

# catalog file of sources, located in the same dir as this script
catalog_file = 'frb.cat' # name dm (pc/cm^3) ra (deg) dec (deg)

def read_in_ignore_chan(filename):
    '''This function reads in the three .ignorechans files used as the ignorechanoption in prepsubband '''
    # Get the directory path where the script is located
    script_dir = os.path.dirname(__file__)

    # Create the full path to the  local file using os.path.join()
    local_file = os.path.join(script_dir, filename)
    if os.path.isfile(local_file):
        with open(local_file, 'r') as f:
            for line in f: # there should only be one line
                line = line.strip()
                ignore_chans = line

            return ignore_chans 
        

def get_nchan(filterbankfile):
    f = SigprocFile(filterbankfile)
    nchan = f.nchans
    return nchan

def load_frb_catalog(catalog_file):
    # Get the directory path where the script is located
    script_dir = os.path.dirname(__file__)

    # Create the full path to the local file using os.path.join()
    local_file = os.path.join(script_dir, catalog_file)

    frb_catalog = {}
    if os.path.isfile(local_file):
        with open(local_file, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue  # Skip comment lines and empty lines
                parts = line.split()
                name = parts[0]
                dm = int(parts[1])
                frb_catalog[name.lower()] = dm  # Store names in lowercase for case-insensitive matching
    return frb_catalog

def guess_dm(filename,):
    frb_catalog = load_frb_catalog(catalog_file)

    filename_lower = filename.lower()  # Convert the filename to lowercase for case-insensitive matching
    for name in frb_catalog:
        if name in filename_lower:  # Check if any catalog name is a substring of the filename
            return frb_catalog[name]  # Return the corresponding DM value if a match is found
    raise ValueError("Could not guess DM from filename: " + filename)



def main(relfilterbankfile, dm, dmrange, display, *, threshold=6, dry_run=False, quiet=False, noclip=False, rfifind=True, ignorechan="", skip_processed=False, zerodm=False, time=30):
    assert(relfilterbankfile.endswith(".fil"))

    stdout = None
    stderr = None
    if quiet:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL

    filterbankfile = os.path.abspath(relfilterbankfile)
    basename = os.path.basename(filterbankfile).rstrip(".fil")
    filterbankpath = os.path.dirname(filterbankfile)

    if skip_processed:
        if os.path.isfile(filterbankpath + "/process/" + basename + "_singlepulse.pdf"):
            print("Already processed:", basename)
            return

    nchan = get_nchan(filterbankfile)

    os.makedirs(filterbankpath + "/process", exist_ok=True)

    orig_cwd = os.getcwd()
    os.chdir(filterbankpath + "/process")

    noclip_option = ""
    if noclip:
        noclip_option = "-noclip"

    outname = basename
    if noclip:
        outname += "_nc"

    # create ignorechan option input
    # reads ignore chan info from master file located in the same dir as this script
    # if band not reconized, prints error
    ignorechanoption = ""
    if ignorechan:
         if "L1_" in filterbankfile:
             ignorechan = read_in_ignore_chan(l1_ignore)
         if 'L2_' in filterbankfile:
             ignorechan = read_in_ignore_chan(l2_ignore)
         if  '_P' in filterbankfile:
             ignorechan = read_in_ignore_chan(p_ignore)
         else:
             print("Could not deduce band from filename, don't know zapchans")

    ignorechanoption = "-ignorechan " + ignorechan

    rfifindoption = ""
    num_rfi_instances = None
    if rfifind:
        rfifind_command = f"rfifind -ncpus 4 -o {outname} {filterbankfile} -time {time}"
        rfifindoption = "-mask " + outname + "_rfifind.mask"
        if not quiet:
            print(rfifind_command)
        if not dry_run:
            with subprocess.Popen(rfifind_command, stdout=subprocess.PIPE, bufsize=1, text=True, shell=True) as p:
                for line in p.stdout:
                    if not quiet:
                        print(line, end='')
                    if 'RFI instances' in line:
                        num_rfi_instances = int(line.split()[2])

    zerodmoption = ""
    if zerodm:
        zerodmoption = "-zerodm"

    prepsubband_command = f"prepsubband -ncpus 4 {noclip_option} {zerodmoption} {ignorechanoption} {rfifindoption} -nsub {nchan} -lodm {dm - dmrange / 2} -dmstep 1 -numdms {dmrange} -o {outname} -nobary {filterbankfile}"

    if not quiet:
        print(prepsubband_command)
    if not dry_run:
        subprocess.run(prepsubband_command, shell=True, stdout=stdout, stderr=stderr)

    num_pulse_candidates = 0
    singlepulse_command = f"single_pulse_search.py -b -t {threshold} {outname}*.dat"
    if not quiet:
        print(singlepulse_command)
    if not dry_run:
        with subprocess.Popen(singlepulse_command, stdout=subprocess.PIPE, bufsize=1, text=True, shell=True) as p:
            for line in p.stdout:
                if not quiet:
                    print(line, end='')
                if "pulse candidates" in line:
                    num_pulse_candidates += int(line.split()[1])

    central_singlepulse_file = f"{basename}_DM{dm:.2f}.singlepulse"
    if not dry_run:
        try:
            with open(central_singlepulse_file, "rb") as f:
                num_pulse_candidates_exact_dm = max(sum(1 for _ in f) - 1, 0)
        except FileNotFoundError:
            num_pulse_candidates_exact_dm = "error"

    ps2pdf_command = f"ps2pdf {outname}_singlepulse.ps"
    if not quiet:
        print(ps2pdf_command)
    if not dry_run:
        subprocess.run(ps2pdf_command, shell=True, stdout=stdout, stderr=stderr)

    if display:
        evince_command = f"evince {outname}_singlepulse.pdf"
        print(evince_command)
        if not dry_run:
            subprocess.run(evince_command, shell=True, stderr=subprocess.DEVNULL)

    if not dry_run:
        with open("process_log.csv", "a") as f:
            print(os.path.basename(filterbankfile), os.getlogin(), datetime.now().isoformat(), num_rfi_instances, num_pulse_candidates, num_pulse_candidates_exact_dm, sep='\t', file=f)

    if not dry_run:
        if num_pulse_candidates < 200:
            if not quiet:
                print(f"Going to create <200 candidates total for all DMs")
            for singlepulse_file in sorted(glob(f"{basename}_DM*.singlepulse")):
                make_candidates_for_singlepulsefile(filterbankfile, singlepulse_file, sigma=threshold)
        elif num_pulse_candidates_exact_dm != "error" and num_pulse_candidates_exact_dm < 1000:
            if not quiet:
                print(f"Going to create {num_pulse_candidates_exact_dm} candidates for central DM")
            make_candidates_for_singlepulsefile(filterbankfile, central_singlepulse_file, sigma=threshold)
        else:
            print(f"Not making {num_pulse_candidates_exact_dm} candidates for {basename}.fil")
    else:
        print("Create candidates for {central_singlepulse_file}")

    os.chdir(orig_cwd)






def init_environment():
    os.environ["PATH"] = os.environ["PATH"] + ":/home_local/camrasdemo/psrsoft/usr/bin"
    os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ":/home_local/camrasdemo/psrsoft/usr/share/python"
    os.environ["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "") + ":/home_local/camrasdemo/psrsoft/usr/lib"
    os.environ["TEMPO"] = "/home_local/camrasdemo/psrsoft/usr/share/tempo"
    os.environ["TEMPO2"] = "/home_local/camrasdemo/psrsoft/usr/share/tempo2"
    os.environ["PGPLOT_DIR"] = "/home_local/camrasdemo/psrsoft/usr/share/pgplot"
    os.environ["PGPLOT_FONT"] = "/home_local/camrasdemo/psrsoft/usr/share/pgplot/grfont.dat"
    os.environ["PGPLOT_RGB"] = "/home_local/camrasdemo/psrsoft/usr/share/pgplot/rgb.txt"
    os.environ["PGPLOT_BACKGROUND"] = "white"
    os.environ["PGPLOT_FOREGROUND"] = "black"

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("filterbankfiles", nargs="+")
    parser.add_argument("--display", "-d", help="Display result in Evince", action="store_true")
    parser.add_argument("--dm", "-dm", help="Center DM (the DM which we expect)", type=float)
    parser.add_argument("--dmrange", "-dmrange", help="Total DM range, default 20", default=20, type=int)
    parser.add_argument("--threshold", "-t", help="Sigma threshold for single_pulse_search", default=6, type=float)
    parser.add_argument("--quiet", "-q", help="Quiet mode", action='store_true')
    parser.add_argument("--noclip", "-noclip", help="Pass -noclip to prepsubband", action='store_true')
    parser.add_argument("--time", "-time", help="rfifind seconds to integrate (default 30)", default=30, type=int)
    parser.add_argument("--no-rfifind", "-no-rfifind", help="Skip rfifind to create RFI mask", action='store_false')
    parser.add_argument("--ignorechan", "-ignorechan", help="Ignorechan", default="")
    parser.add_argument("--dry-run", action='store_true')
    parser.add_argument("--skip-processed", "-s", action='store_true')
    parser.add_argument("--zerodm", action='store_true')

    init_environment()
    args = parser.parse_args()

    if args.dm is None:
        for filterbankfile in args.filterbankfiles:
            try:
                _ = guess_dm(filterbankfile)
            except ValueError:
                raise ValueError("-dm not given and could not guess DM for " + filterbankfile)
        print("Will use known DMs")

    for filterbankfile in tqdm(args.filterbankfiles, disable=(not args.quiet)):
        dm = args.dm
        if dm is None:
            dm = guess_dm(filterbankfile)

        try:
            main(filterbankfile, dm, args.dmrange, args.display, threshold=args.threshold, dry_run=args.dry_run, quiet=args.quiet, noclip=args.noclip, rfifind=args.no_rfifind, ignorechan=args.ignorechan, skip_processed=args.skip_processed, zerodm=args.zerodm, time=args.time)
        except:
            print("Error with", filterbankfile)
