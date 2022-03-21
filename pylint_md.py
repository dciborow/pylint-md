"""pylint markdown conversion tool"""

import glob
import subprocess
import json
import sys
import getopt
from collections import Counter

def pylint_markdown(location, output_path):
    """Main conversion engine"""

    totals = {'error': 0, 'warning': 0, 'refactor': 0, 'convention': 0}

    markdown_summary = [f'# Analysis of folder {location}']
    analysisfiles = glob.glob(f'{location}/**/*.py', recursive=True)
    filecount = len(analysisfiles)

    print(f'Performing analysis of {filecount} file(s)')

    markdown_files = []
    for filepath in glob.glob(f'{location}/**/*.py', recursive=True):
        print(f'Processing file {filepath}')

        markdown_files.extend((f'## {filepath}', '### Summary'))
        json_counter = Counter()
        lint_json = None

        proc = subprocess.Popen(
            f"pylint {filepath} -f json --persistent=n --score=y",
            stdout=subprocess.PIPE,
            shell=True,
        )

        (out, _err) = proc.communicate()
        if out and  out.strip():
            lint_json = json.loads(out)
            json_counter = Counter(player['type'] for player in lint_json)

        markdown_files.extend(
            (
                '|Type|Number|',
                '|-|-|',
                f"|error|{json_counter['error']}|",
                f"|warning|{json_counter['warning']}|",
                f"|refactor|{json_counter['refactor']}|",
                f"|convention|{json_counter['convention']}|",
            )
        )

        # Add to the counters
        totals['error'] += json_counter['error']
        totals['warning'] += json_counter['warning']
        totals['refactor'] += json_counter['refactor']
        totals['convention'] += json_counter['convention']

        markdown_files.append('\n### Pylint messages\n')
        if lint_json is not None:
            markdown_files.extend(
                '* Line: {} is {}[{}] in {}.py\n'.format(
                    lint['line'],
                    lint['message'],
                    lint['message-id'],
                    lint['module'],
                )
                for lint in lint_json
            )

        else:
            markdown_files.append('* No issues found')

        markdown_files.append('---')

    markdown_summary.extend(
        ('|Item|Number|', '|-|-|', f'|files processed|{filecount}|')
    )

    markdown_summary.append(f"|errors|{totals['error']}|")
    markdown_summary.append(f"|warnings|{totals['warning']}|")
    markdown_summary.append(f"|refactors|{totals['refactor']}|")
    markdown_summary.extend((f"|conventions|{totals['convention']}|", '---'))
    print(
        f"errors={totals['error']};warnings={totals['warning']};refactors={totals['refactor']};conventions={totals['convention']}"
    )


    export_as_markdown(output_path, (markdown_summary + markdown_files))

def export_as_markdown(output_path, markdown):
    """Export the markdown content"""

    print(f'Generating markdown file: {output_path}')
    with open(output_path, 'w') as out_file:
        for row in markdown:
            out_file.write(row+'\n')

def main(argv):
    """Main function for pylint_md to process the file arguments """

    location = None
    output_file = None
    try:
        opts, _args = getopt.getopt(argv, "hl:o:", ["rlocation=", "ooutput_file="])
    except getopt.GetoptError:
        print('pylint_md.py -l <location> -o <output_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('pylint_md -l <location> -o <output_file>')
            sys.exit()
        elif opt in ("-l", "--llocation"):
            location = arg
        elif opt in ("-o", "--oooutput_file"):
            output_file = arg
    print(f'Location  is {location}')
    print(f'Output file is {output_file}')

    if location is not None and output_file is not None:
        pylint_markdown(location, output_file)

if __name__ == "__main__":
    main(sys.argv[1:])
