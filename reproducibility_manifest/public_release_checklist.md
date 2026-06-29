# Public Release Checklist

Before exporting this branch to a new public GitHub project:

- [ ] Run `python scripts/verify_public_package.py`.
- [ ] Run `python -m unittest discover -s tests -p "test_*.py"`.
- [ ] Run `scripts/reproduce_analysis.ps1` or the equivalent Python commands.
- [ ] Confirm no private Windows paths remain in public text files.
- [ ] Confirm no DNI, credentials, `.env` secrets or local IP-only notes are exposed.
- [ ] Remove private article drafts, downloaded papers and thesis-only Word/PDF artifacts if they are not intended for public release.
- [ ] Decide whether raw logs will be deposited externally and update `DATA_AVAILABILITY.md`.
- [ ] Tag the public release and archive it if a DOI is needed.
