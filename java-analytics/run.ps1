param(
    [Parameter(Mandatory=$true)][string]$Scenario,
    [Parameter(Mandatory=$true)][string]$Session,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference = 'Stop'
$jdkBin = if ($env:JAVA_HOME) { Join-Path $env:JAVA_HOME 'bin' } else {
    Split-Path (Get-Command javac -CommandType Application -ErrorAction Stop).Source
}
$javac = Join-Path $jdkBin 'javac.exe'
$java = Join-Path $jdkBin 'java.exe'
$build = Join-Path $PSScriptRoot 'build'
$jar = Join-Path $build 'gson-2.13.2.jar'
$expectedHash = 'DD0CE1B55A3ED2080CB70F9C655850CDA86C206862310009DCB5E5C95265A5E0'
New-Item -ItemType Directory -Force $build | Out-Null
if (!(Test-Path -LiteralPath $jar) -or (Get-FileHash -LiteralPath $jar).Hash -ne $expectedHash) {
    $url = 'https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.13.2/gson-2.13.2.jar'
    Invoke-WebRequest -UseBasicParsing $url -OutFile $jar
    if ((Get-FileHash -LiteralPath $jar).Hash -ne $expectedHash) {
        throw 'Gson download did not match the expected SHA-256 digest'
    }
}
$sources = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'src/training') -Filter '*.java' |
    ForEach-Object FullName)
& $javac --release 11 -encoding UTF-8 -cp $jar -d $build @sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $java -cp "$build;$jar" training.Main $Scenario $Session $Output
exit $LASTEXITCODE