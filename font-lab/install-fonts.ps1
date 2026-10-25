# 安装 ZONE skin 的中文字体（当前用户，无需管理员）
#
#   powershell -ExecutionPolicy Bypass -File .\install-fonts.ps1
#   powershell -ExecutionPolicy Bypass -File .\install-fonts.ps1 -Dir D:\fonts
#
# 装的是 Noto Sans Mono CJK SC 的 Regular + Bold（皮肤 CSS 里点名的那个字族）。
# 不装也能用，中文会回退到 Maple Mono CN / 微软雅黑，字宽和字形都不一样。
# 可以重复运行：已装好的会跳过，不会去动正在被占用的字体文件。

param(
    [string]$Dir = (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts')
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path $here 'fonts'
$dstDir = $Dir
$regKey = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'

$faces = @(
    @{ file = 'NotoSansMonoCJKsc-Regular.otf'; name = 'Noto Sans Mono CJK SC (OpenType)' },
    @{ file = 'NotoSansMonoCJKsc-Bold.otf';    name = 'Noto Sans Mono CJK SC Bold (OpenType)' }
)

New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
$changed = 0
$skipped = 0

foreach ($face in $faces) {
    $from = Join-Path $src $face.file
    $to = Join-Path $dstDir $face.file

    if (-not (Test-Path $from)) {
        Write-Host "跳过：源文件缺失 $($face.file)" -ForegroundColor Yellow
        continue
    }

    $registered = (Get-ItemProperty -Path $regKey -Name $face.name -ErrorAction SilentlyContinue).($face.name)
    if ($registered -eq $to -and (Test-Path $to)) {
        Write-Host "已安装，跳过：$($face.name)" -ForegroundColor DarkGray
        $skipped++
        continue
    }

    # 只在文件不在时才复制：文件可能正被应用占用，覆盖会失败。
    if (-not (Test-Path $to)) {
        try {
            Copy-Item -LiteralPath $from -Destination $to -Force
        } catch {
            Write-Host "无法写入 $to" -ForegroundColor Red
            Write-Host "字体文件被占用：先完全退出 DeepSeek Harness，再运行一次本脚本。" -ForegroundColor Yellow
            exit 1
        }
    }
    New-ItemProperty -Path $regKey -Name $face.name -Value $to -PropertyType String -Force | Out-Null
    Write-Host "已登记 $($face.name)" -ForegroundColor Green
    $changed++
}

Write-Host ""
if ($changed -eq 0 -and $skipped -eq 0) {
    Write-Host "没有安装任何字体（检查 fonts/ 目录）。" -ForegroundColor Yellow
} elseif ($changed -eq 0) {
    Write-Host "两个字体本来就在，无需改动。" -ForegroundColor Cyan
} else {
    Write-Host "完成。重启 DeepSeek Harness 后中文才会用上新字体。" -ForegroundColor Cyan
    Write-Host "（渲染进程只在启动时枚举系统字体，重启一次即可。）"
}
