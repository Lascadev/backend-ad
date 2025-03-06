param (
    [string]$certPath,
    [string]$password
)

# Importar el certificado .p12
$securePassword = ConvertTo-SecureString -String $password -Force -AsPlainText
Import-PfxCertificate -FilePath $certPath -Password $securePassword -CertStoreLocation Cert:\CurrentUser\My