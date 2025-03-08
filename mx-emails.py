import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_MX = "smtpin.rzone.de"  # Target MX host to filter emails

def load_emails_from_file(file_path):
    """Load emails from a file, line by line."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def extract_domain(email):
    """Extract the domain from an email address."""
    return email.split('@')[-1].lower()

def resolve_mx_servers(domain):
    """Resolve all MX servers for a given domain and return the list."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange).rstrip('.') for mx in mx_records]  # Get all MX hosts
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return []
    except Exception as e:
        print(f"Error resolving MX for {domain}: {e}")
        return []

def process_email(email, output_file):
    """Process a single email and write it to the file if it matches 'smtpin.rzone.de'."""
    domain = extract_domain(email)
    mx_hosts = resolve_mx_servers(domain)

    if TARGET_MX in mx_hosts:
        print(f"✅ MATCH: {email} -> {mx_hosts}")  # Debugging
        with open(output_file, 'a', encoding='utf-8') as log_file:  # Open in append mode
            log_file.write(email + "\n")  # Save immediately

def check_emails_and_save_valid_hosts(input_file, output_file, max_workers=10):
    """Check emails for the specific MX host concurrently and save matching emails."""
    emails = load_emails_from_file(input_file)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_email, email, output_file) for email in emails]
        for future in as_completed(futures):
            future.result()  # Ensure all tasks complete

# Example usage
input_file_path = "emails.txt"  # Path to the file with email addresses
output_file_path = "rzone_emails.txt"  # Path to save matching emails

# Check emails and save only those with 'smtpin.rzone.de' as MX host
check_emails_and_save_valid_hosts(input_file_path, output_file_path, max_workers=5)
