import base64
import re
from datetime import datetime
from pathlib import Path

from ghapi.all import GhApi
from ghapi.page import pages

owner = "ev-map"
repo = "EVMap"
langs = {
    'en': 'en-US',
    'de': 'de-DE'
}
date_formats = {
    'en': '%Y-%m-%d',
    'de': '%d.%m.%Y'
}
output_path = Path("_i18n")
output_filename = "changelog.md"

api = GhApi(owner=owner, repo=repo)

def get_releases():
    releases = api.repos.list_releases(per_page=100)
    last_page = api.last_page()
    if last_page > 0:
        releases = pages(api.repos.list_releases, last_page, per_page=100).concat()
    return releases


def get_content(path, ref):
    content = api.repos.get_content(path, ref=ref)
    return base64.b64decode(content['content']).decode('utf-8')


def parse_date(date: str):
    return datetime.fromisoformat(date.replace('Z', '+00:00'))


def extract_changelogs(tag):
    try:
        build_gradle = get_content("app/build.gradle", tag)
        match = re.search(r'versionCode (\d+)', build_gradle)
        if not match:
            return None

        version_code = int(match.group(1))

        changelogs = {}
        for lang in langs:
            changelogs[lang] = get_content(f"fastlane/metadata/android/{langs[lang]}/changelogs/{version_code}.txt", tag)
        return changelogs
    except:
        return None


for lang in langs:
    (output_path / lang).mkdir(exist_ok=True)

output_files = {
    lang: open(output_path / lang / output_filename, 'w', encoding='utf-8') for lang in langs
}

print('generating changelog...')
releases = get_releases()
for release in releases:
    tag = release['tag_name']
    if release['draft'] or release['prerelease'] or 'beta' in tag:
        continue

    print(tag)

    date = parse_date(release['published_at'])
    for lang in langs:
        output_files[lang].write(f"# Version {tag}\n")
        output_files[lang].write(f"*{date.strftime(date_formats[lang])}*\n\n")

    changelogs = extract_changelogs(tag)
    body = release['body']
    if changelogs is not None:
        for lang in langs:
            output_files[lang].write(changelogs[lang] + "\n\n")
    elif body is not None:
        for lang in langs:
            output_files[lang].write(body + "\n\n")
    else:
        for lang in langs:
            output_files[lang].write("\n\n")