param(
    [int]$Port = 8501,
    [string]$Hostname = "",
    [string]$TunnelName = "radar-dashboard"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$LogDir = Join-Path $ProjectRoot "logs"
$StreamlitOutLog = Join-Path $LogDir "streamlit-out.log"
$StreamlitErrLog = Join-Path $LogDir "streamlit-err.log"
$CloudflaredLog = Join-Path $LogDir "cloudflared.log"
$CloudflaredOutLog = Join-Path $LogDir "cloudflared-out.log"
$CloudflaredErrLog = Join-Path $LogDir "cloudflared-err.log"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Remove-Item $StreamlitOutLog, $StreamlitErrLog, $CloudflaredLog, $CloudflaredOutLog, $CloudflaredErrLog -Force -ErrorAction SilentlyContinue

$Cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $Cloudflared) {
    Write-Host "cloudflared não está instalado ou não está no PATH." -ForegroundColor Yellow
    Write-Host "Instale pelo winget: winget install --id Cloudflare.cloudflared"
    exit 1
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

function Test-Streamlit {
    param([int]$Port)
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/_stcore/health" -UseBasicParsing -TimeoutSec 5
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

$StartedStreamlit = $false
$StreamlitProcess = $null

if (Test-Streamlit -Port $Port) {
    Write-Host "Streamlit já está ativo em http://127.0.0.1:$Port." -ForegroundColor Green
} else {
    Write-Host "Iniciando Streamlit em http://127.0.0.1:$Port ..." -ForegroundColor Cyan
    $StreamlitArgs = @(
        "-m", "streamlit", "run", "app.py",
        "--server.address", "127.0.0.1",
        "--server.port", "$Port",
        "--server.headless", "true"
    )

    $StreamlitProcess = Start-Process `
        -FilePath $Python `
        -ArgumentList $StreamlitArgs `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $StreamlitOutLog `
        -RedirectStandardError $StreamlitErrLog `
        -PassThru `
        -WindowStyle Hidden
    $StartedStreamlit = $true

    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Streamlit -Port $Port) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        Write-Host "O Streamlit não respondeu em http://127.0.0.1:$Port." -ForegroundColor Red
        Write-Host "Veja os logs:"
        Write-Host "  $StreamlitOutLog"
        Write-Host "  $StreamlitErrLog"
        if ($StreamlitProcess) {
            Stop-Process -Id $StreamlitProcess.Id -Force -ErrorAction SilentlyContinue
        }
        exit 1
    }
}

Write-Host ""
Write-Host "Dashboard local OK: http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "Abrindo Cloudflare Tunnel..." -ForegroundColor Cyan
Write-Host "Log do túnel: $CloudflaredLog"
Write-Host "Se a URL pública não abrir, confira se este terminal continua aberto e se o log mostra 'Registered tunnel connection'."
Write-Host ""

if ([string]::IsNullOrWhiteSpace($Hostname)) {
    Write-Host "Aguarde a linha com a URL pública https://...trycloudflare.com" -ForegroundColor Yellow
    Write-Host "Enquanto esta janela ficar aberta, a URL continuará funcionando."
    Write-Host ""
    $CloudflaredArgs = @(
        "tunnel",
        "--no-autoupdate",
        "--url", "http://127.0.0.1:$Port",
        "--logfile", $CloudflaredLog,
        "--loglevel", "info"
    )
} else {
    Write-Host "Usando domínio fixo: $Hostname" -ForegroundColor Yellow
    Write-Host "Pré-requisito: rode antes 'cloudflared tunnel login' e configure o domínio na Cloudflare."
    Write-Host ""
    $CloudflaredArgs = @(
        "tunnel",
        "--no-autoupdate",
        "--name", $TunnelName,
        "--url", "http://127.0.0.1:$Port",
        "--hostname", $Hostname,
        "--logfile", $CloudflaredLog,
        "--loglevel", "info"
    )
}

$CloudflaredProcess = Start-Process `
    -FilePath $Cloudflared.Source `
    -ArgumentList $CloudflaredArgs `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $CloudflaredOutLog `
    -RedirectStandardError $CloudflaredErrLog `
    -PassThru

try {
    $PublicUrl = $null
    if ([string]::IsNullOrWhiteSpace($Hostname)) {
        for ($i = 0; $i -lt 45; $i++) {
            Start-Sleep -Seconds 1
            $logText = ""
            foreach ($path in @($CloudflaredLog, $CloudflaredOutLog, $CloudflaredErrLog)) {
                if (Test-Path $path) {
                    $logText += "`n" + (Get-Content $path -Raw -ErrorAction SilentlyContinue)
                }
            }

            $match = [regex]::Match($logText, "https://[a-zA-Z0-9-]+\.trycloudflare\.com")
            if ($match.Success) {
                $PublicUrl = $match.Value
                break
            }

            if ($CloudflaredProcess.HasExited) {
                break
            }
        }

        if ($PublicUrl) {
            Write-Host ""
            Write-Host "URL pública do dashboard:" -ForegroundColor Green
            Write-Host $PublicUrl -ForegroundColor Green
            Write-Host ""
            Write-Host "Mantenha esta janela aberta. Para encerrar, pressione Ctrl+C."
        } else {
            Write-Host "Não consegui capturar a URL pública automaticamente." -ForegroundColor Red
            Write-Host "Veja o log: $CloudflaredLog"
        }
    } else {
        Write-Host ""
        Write-Host "Dashboard publicado em: https://$Hostname" -ForegroundColor Green
        Write-Host "Mantenha esta janela aberta. Para encerrar, pressione Ctrl+C."
    }

    Wait-Process -Id $CloudflaredProcess.Id
} finally {
    if ($CloudflaredProcess -and -not $CloudflaredProcess.HasExited) {
        Stop-Process -Id $CloudflaredProcess.Id -Force -ErrorAction SilentlyContinue
    }

    if ($StartedStreamlit -and $StreamlitProcess) {
        Write-Host "Encerrando Streamlit iniciado por este script..." -ForegroundColor Cyan
        Stop-Process -Id $StreamlitProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
