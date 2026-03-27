# UPS-Lite Patch Bundle

This bundle contains a patched `ups_lite.py` plugin that adds support for XiaoJ/ACE UPS Lite boards using the `0x62` (`CW2015`) battery gauge and prevents false shutdowns caused by invalid zero readings

Files:

- `ups_lite.py` - the current modified version of the original plugin  
  https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
- `ups_lite.patch` - a unified diff against the original `ups_lite.py`  
  https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
- `apply_patch.py` - a safe script to apply the patch to the original file

What the patch changes:

- auto-detection of `0x62 / cw2015` and `0x36 / max17040`
- initialization for `CW2015`
- correct `voltage` and `capacity` reading for `0x62`
- protection against false shutdown when the battery reading is invalid

Expected original file:

- `/usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py`

1. Apply with the script:

```bash
cd /path/to/ups_lite_repair
sudo python3 apply_patch.py
```

2. Or with an explicit path:

```bash
sudo python3 apply_patch.py /usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py
```

What the script does:

- verifies that the target file matches the expected original version
- creates a backup next to the target file: `ups_lite.py.bak`
- writes the patched version

Manual patch application:

```bash
sudo patch /usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py < ups_lite.patch
```