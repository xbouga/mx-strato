import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_emails_from_file(file_path):
    """Load emails from a file, line by line."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def extract_domain(email):
    """Extract the domain from an email address."""
    return email.split('@')[-1]

def resolve_mx_server(domain):
    """Resolve MX server for the given domain and return the host."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(mx_records[0].exchange).rstrip('.')  # Get the highest priority MX record
        return mx_host
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return None
    except Exception as e:
        print(f"Error resolving MX for {domain}: {e}")
        return None

def process_email(email):
    """Process a single email to check its MX records and exclude specific hosts."""
    domain = extract_domain(email)
    mx_host = resolve_mx_server(domain)
    # Return the email only if it has a valid MX host containing "rzone.de" or "strato"
    if mx_host and ("rzone.de" in mx_host or "strato" in mx_host):
        return f"{email}: Valid MX Host ({mx_host})"
    return None

def check_emails_and_save_valid_hosts(input_file, output_file, max_workers=10):
    """Check emails for valid MX records concurrently and save only valid hosts."""
    emails = load_emails_from_file(input_file)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Launch tasks for each email
        future_to_email = {executor.submit(process_email, email): email for email in emails}
        for future in as_completed(future_to_email):
            result = future.result()
            if result:
                with open(output_file, 'a', encoding='utf-8') as log_file:
                    log_file.write(result + "\n")
                print(result)

# Example usage
input_file_path = "urls.txt"  # Path to the file with email addresses
output_file_path = "valid_mx_hosts.txt"  # Path to save results

# Check emails and save only valid hosts
check_emails_and_save_valid_hosts(input_file_path, output_file_path, max_workers=1)
