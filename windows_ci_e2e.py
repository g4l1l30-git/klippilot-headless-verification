"""Headless Windows runner proof using original synthetic fixtures only.

Run from an extracted buyer ZIP, with its installed venv interpreter. This does
not establish interactive GUI acceptance or human-footage quality.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run(*args):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError('Subprocess failed; diagnostic checksum '+hashlib.sha256(result.stderr.encode()).hexdigest())
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = Path.cwd()
    fixture = root/'ci-fixtures'
    fixture.mkdir(exist_ok=True)
    audio = (fixture/'speech.wav').resolve()
    # The only speech sent to the hosted test is generated on that runner.
    script = ("Add-Type -AssemblyName System.Speech; "
              "$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              f"$voice.SetOutputToWaveFile('{str(audio).replace(chr(39), chr(39)*2)}'); "
              "$voice.Speak('This video tests an editable storyboard. "
              "The software should preserve this original recording.'); $voice.Dispose()")
    run('powershell', '-NoProfile', '-Command', script)
    source = fixture/'raw.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
        'testsrc2=size=360x640:rate=30', '-i', audio, '-shortest',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', source)
    original = digest(source)
    project = root/'ci-project'
    run(sys.executable, 'engine.py', 'plan', source, project, '--language', 'en')
    plan = json.loads((project/'plan.json').read_text(encoding='utf-8'))
    if not plan['clips'] or not any(c['text'].strip() for c in plan['clips']):
        raise AssertionError('ASR did not produce an editable plan')
    if not (project/'storyboard.html').is_file():
        raise AssertionError('Storyboard missing')
    run(sys.executable, 'engine.py', 'render', project)
    before = digest(project/'result.mp4')
    run(sys.executable, 'engine.py', 'edit', project,
        'Use darker lighting and stronger captions. Make the framing wider.')
    run(sys.executable, 'engine.py', 'render', project)
    after = digest(project/'result.mp4')
    qc = json.loads((project/'qc.json').read_text())
    if before == after or digest(source) != original or qc['decode'] != 'pass':
        raise AssertionError('Render change, source preservation or QC failed')
    report = dict(test='fresh-hosted-Windows-headless', gui_tested=False,
                  private_footage_uploaded=False, asr_clips=len(plan['clips']),
                  original_sha256=original, before_sha256=before,
                  after_sha256=after, qc=qc)
    (root/'ci-evidence.json').write_text(json.dumps(report, indent=2))
    print('KLIPPILOT_CI_EVIDENCE=' + json.dumps(report))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('KLIPPILOT_CI_FAILURE='+type(error).__name__)
        sys.exit(1)
