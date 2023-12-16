from datetime import datetime
import json
import argparse
import scraper

def flush_(out, reverse):
    sr = sorted(out)
    first, last = sr[0], sr[-1]
    _filename = f'/mnt/c/temp/rechecks-{first}-{last}-{datetime.now().strftime("%Y%m%dT%H%M%S")}.json'
    with open(_filename, "w") as fp:
        json.dump(out, fp, indent=4)
    with open(f"/tmp/last{'' if not reverse else 'r'}", "w") as fp:
        fp.write(last)
    print(f"Wrote {_filename}")

def __parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reverse", dest="reverse", action="store_true",
                        default=False, help="Run from back of list")
    return parser.parse_args()


if __name__ == "__main__":
    args = __parse_args()
    
    with open("/mnt/c/tmp/untagged.json") as fp:
        acct_list = json.load(fp)
        if args.reverse:
            acct_list.reverse()
    try:
        with open(f"/tmp/last{'' if not args.reverse else 'r'}") as fp:
            last = fp.read().strip()
            index = acct_list.index(last)
            print(f"last = {last}, index={index}")
    except FileNotFoundError:
        index = 0

    print(f"starting at index = {index}")
    driver = scraper.get_driver("chrome")
    out = {}
    for acct in acct_list[index:]:
        u = scraper.info(driver, acct)
        print(acct)
        out[acct] = u
        if len(out) == 50:
            flush_(out, args.reverse)
            out = {}
    flush_(out, args.reverse)
