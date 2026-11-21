import sys
def main():
    import json,pathlib,subprocess,sys
    root=pathlib.Path('buyer').resolve()
    steps=[['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'install.ps1')],
           [str(root/'.venv/Scripts/python.exe'),str(pathlib.Path('windows_ci_e2e.py').resolve())]]
    for index,step in enumerate(steps):
        result=subprocess.run(step,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if result.returncode:
            print('HEADLESS_STEP_FAILED='+str(index));sys.exit(1)
        for line in result.stdout.splitlines():
            if line.startswith('KLIPPILOT_CI_EVIDENCE='):
                data=json.loads(line.split('=',1)[1])
                assert data.get('private_footage_uploaded') is False and data.get('gui_tested') is False
                qc=data["qc"]
                safe=dict(test="fresh-hosted-Windows-headless",gui_tested=False,private_footage_uploaded=False,
                          asr_clips=int(data["asr_clips"]),
                          qc={k:qc[k] for k in ["decode","black_seconds","peak_db","planned_seconds","actual_seconds","sha256"]})
                import re
                assert safe["qc"]["decode"]=="pass" and re.fullmatch("[a-f0-9]{64}",safe["qc"]["sha256"])
                for k in ["black_seconds","peak_db","planned_seconds","actual_seconds"]:safe["qc"][k]=float(safe["qc"][k])
                print('KLIPPILOT_CI_EVIDENCE='+json.dumps(safe))
    print('HEADLESS_INSTALL_ASR_STORYBOARD_EDIT_RENDER_QC_PASS')
try:
    main()
except Exception as error:
    print('HARNESS_FAILED='+type(error).__name__)
    sys.exit(1)
