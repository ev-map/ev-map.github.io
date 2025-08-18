import requests
import html

from pathlib import Path

from ghapi.all import GhApi
from ghapi.page import pages

from collections import defaultdict

owner = "ev-map"
repo = "EVMap"
output_path = Path("_includes")
output_filename = "licenses.md"

api = GhApi(owner=owner, repo=repo)

output_file = open(output_path / output_filename, 'w', encoding='utf-8')

print('generating OSS licenses...')
release = api.repos.get_latest_release()
asset = next(a for a in release["assets"] if a["name"] == "aboutlibraries.json")

library_data = requests.get(asset["browser_download_url"]).json()

num_libs_by_license = defaultdict(lambda: 0)

output_file.write("# Libraries\n")
for library in library_data["libraries"]:
    output_file.write(f"## {library['name'] if 'name' in library else library['uniqueId']} {library['artifactVersion']}\n")
    devs = [dev['name'] for dev in library['developers'] if 'name' in dev]
    if len(devs) > 0:
        output_file.write(f"*{', '.join(devs)}*<br>")

    licenses = []
    for lic in library['licenses']:
        name = library_data['licenses'][lic]['name']
        link = f"#license_{lic}" if "content" in library_data['licenses'][lic] else library_data['licenses'][lic]["url"]
        result = f"[{name}]({link})"
        licenses.append(result)

    output_file.write(f"License: {', '.join(licenses)}\n")
    output_file.write("\n")

    for lic in library['licenses']:
        num_libs_by_license[lic] += 1

output_file.write("# Licenses\n")
libs_sorted = sorted(num_libs_by_license.keys(), key=lambda lib: num_libs_by_license[lib], reverse=True)
for key in libs_sorted:
    license = library_data['licenses'][key]
    if not 'content' in license:
        continue
    output_file.write(f"<h2 id=\"license_{key}\">{license['name']}</h2>\n")
    output_file.write("<pre>" + html.escape(license['content']) + "</pre>\n")
    output_file.write("\n")


#
#
#     tag = release['tag_name']
#     if release['draft'] or release['prerelease'] or 'beta' in tag:
#         continue
#
#     print(tag)
#
#     date = parse_date(release['published_at'])
#     for lang in langs:
#         output_files[lang].write(f"# Version {tag}\n")
#         output_files[lang].write(f"*{date.strftime(date_formats[lang])}*\n\n")
#
#     changelogs = extract_changelogs(tag)
#     body = release['body']
#     if changelogs is not None:
#         for lang in langs:
#             output_files[lang].write(changelogs[lang] + "\n\n")
#     elif body is not None:
#         for lang in langs:
#             output_files[lang].write(body + "\n\n")
#     else:
#         for lang in langs:
#             output_files[lang].write("\n\n")