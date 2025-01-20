import requests
import os
import subprocess
from dotenv import load_dotenv

# Načítanie premenných z .env súboru
load_dotenv()

# Konfigurácia
URL = os.getenv("URL", "http://example.unimus")  # Získanie základnej URL z ENV premenných
API_ENDPOINT = "/api/v2/devices"  # Konštantná časť URL
BASE_URL = f"{URL}{API_ENDPOINT}"  # Kombinácia základnej URL a endpointu


BEARER_TOKEN = os.getenv("BEARER_TOKEN", "vloz_tvoj_bearer_token")  # Získanie tokenu z ENV premenných

community = os.getenv("Community", "public")

SNMP_VERSION = "2"
MRTG_CONF_DIR = "/tmp/mrtg-gen"
BACKUP_DIR = "/var/www/mrtg.bak"
CURRENT_MRTG_DIR = "/var/www/html/mrtg"
SCRIPT_DIR = "/app"
CONFIG_FILE_PATH = f"{SCRIPT_DIR}/mrtgconf.sh"
INDEX_FILE_PATH = f"{SCRIPT_DIR}/mrtgindex.sh"




# Hlavičky pre autentifikáciu
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Parametre dotazu
params = {
    "page": 0,       # Počiatočný index stránky
    "size": 20,      # Počet zariadení na stránku
    "attr": "s,c"   # Voliteľné atribúty (schedule, credential)
}

def prepare_directories():
    os.makedirs(MRTG_CONF_DIR, exist_ok=True)
    if os.path.exists(BACKUP_DIR):
        subprocess.run(["rm", "-rf", BACKUP_DIR])
    subprocess.run(["cp", "-r", CURRENT_MRTG_DIR, BACKUP_DIR])




try:
    # Poslanie GET požiadavky na API
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Kontrola HTTP status kódu
    if response.status_code == 200:
        # Spracovanie JSON odpovede
        data = response.json()
        devices = data.get("data", [])

        prepare_directories()
        mrtgconf = "/usr/bin/cfgmaker --output=/tmp/mrtg-gen/mrtg.cfg.new --global \"Interval: 5\" --global \"Forks: 4\" --global \"options[_]: growright,bits\" --ifdesc=descr --ifdesc=name --ifdesc=alias --show-op-down --no-down --subdirs=HOSTNAME__SNMPNAME"

        for device in devices:
            ip = device['address']
#            community = device.get('description', 'public')  # Default snmp community if not available
#            community = "public" 
            mrtg_entry = f"{community}@{ip}:::::{SNMP_VERSION}"
            mrtgconf += f" {mrtg_entry}"

            file_content = f"/usr/bin/cfgmaker --output=/tmp/mrtg-gen/mrtg.cfg.new --global \"Interval: 5\" --global \"Forks: 4\" --global \"options[_]: growright,bits\" --ifdesc=descr --show-op-down --ifdesc=name --ifdesc=alias --no-down --subdirs=HOSTNAME__SNMPNAME {mrtg_entry};"
            with open(INDEX_FILE_PATH, "w") as index_file:
                index_file.write(file_content)

            subprocess.run(["bash", INDEX_FILE_PATH])
            subprocess.run(["indexmaker", f"--output={CURRENT_MRTG_DIR}/{ip}.html", "/tmp/mrtg-gen/mrtg.cfg.new"])

        with open(CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(mrtgconf)

        subprocess.run(["bash", CONFIG_FILE_PATH])
        subprocess.run(["killall", "mrtg"])
        subprocess.run(["mv", "/etc/mrtg/mrtg.cfg", "/etc/mrtg/mrtg.cfg.old"])
        subprocess.run(["cp", "-f", "/tmp/mrtg-gen/mrtg.cfg.new", "/etc/mrtg/mrtg.cfg"])
        subprocess.run(["rm", "-rf", MRTG_CONF_DIR])

        print("MRTG konfigurácia úspešne aktualizovaná.")
    else:
        print(f"Chyba: {response.status_code} - {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Chyba pripojenia: {e}")
