# DSH ZONE Skin

黑橙硬件风的 [DeepSeek Harness](https://github.com/deepseek-ai) Web UI 皮肤插件。
A black-and-orange hardware styling client plugin for the DeepSeek Harness Web UI:
graphite chassis, hot orange accents, sticker geometry, hazard stripes and an LED
device bar — with four colorways (zone orange / ember / hazard / cobalt) on two
canvases (blacksite / cream).

## Layout

| Path | Contents |
| --- | --- |
| [`package/`](package/README.md) | The plugin itself (`@local/dsh-zone-skin`) — token layer, stylesheet, slots, tests. Start at its [README](package/README.md); field notes in [NOTES.md](package/NOTES.md), contributor notes in [AGENTS.md](package/AGENTS.md). |
| [`font-lab/`](font-lab/README.md) | The Chinese-font study workspace: specimen sheets, measurements and the installable font files. |
| `tools/` | Python helpers used to measure fonts and render the specimen sheets. |

## Quick start

1. Install the Chinese face once per machine (not bundled with the plugin —
   31.8 MB of OTF):

   ```powershell
   powershell -ExecutionPolicy Bypass -File font-lab\install-fonts.ps1
   ```

2. Point a DSH profile at `package/` (`link:` for live editing), `pnpm install`,
   restart the desktop app. Exact commands: [package/AGENTS.md → Packaging](package/AGENTS.md).

## Checks

```sh
cd package && npm run check
```

## License

Plugin code: MIT. Font files in `font-lab/fonts/` keep their respective upstream
licenses (SIL OFL 1.1 for Noto / Sarasa / Maple / Smiley Sans; free-commercial
licenses from Huawei / Xiaomi / Alibaba for HarmonyOS Sans / MiSans / PuHuiTi).
