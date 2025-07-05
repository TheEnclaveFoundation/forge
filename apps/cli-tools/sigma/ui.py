from forge.packages.common.ui import eprint, clear_screen, Colors

def print_banner():
    clear_screen()
    eprint(f"\n{Colors.CYAN}--- Σ ---{Colors.RESET}\n")

def print_summary(repos_scraped_count, files_forged_count, output_dest):
    eprint(f"\n{Colors.GREEN}{Colors.BOLD}✨ Context Forged.{Colors.RESET}")
    eprint(f"  {Colors.GREY}- Repos Scraped: {Colors.PURPLE}{repos_scraped_count}{Colors.RESET}")
    eprint(f"  {Colors.GREY}- Files Forged:  {Colors.PURPLE}{files_forged_count}{Colors.RESET}")
    eprint(f"  {Colors.GREY}- Output:        {Colors.CYAN}{output_dest}{Colors.RESET}")


