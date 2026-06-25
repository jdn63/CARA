# NCES Data Folder

This folder holds the NCES SSOCS (School Survey on Crime and Safety) data used
for the active shooter risk calculations.

Required file:
- pu_ssocs20.sav  (SSOCS 2019-2020 public-use data, SPSS format)

The processor (utils/nces_ssocs_processor.py) reads pu_ssocs20.sav via
pyreadstat. Only this file is needed. Other distribution formats (Stata .dta,
SAS .sas7bdat, raw ASCII .dat, the .do/.sas/.sps import scripts, the codebook
PDF, and the metadata spreadsheet) are intentionally excluded from the repo and
from release builds to keep it lean.
