# QR Bill Tool
A tool, based around the [swiss-qr-bill](https://github.com/claudep/swiss-qr-bill/) package, that can create qr bills for a local sports club.

## Functionality
- Simple streamlit UI to configure and create single bills as well as in bulk from a csv file.
- Ability to create new debtors as well as use predefined recurring debtors.
- Specify debtor, creditor, amount, payment reason as well as the contents of the accompanying letter.
- Create the qr bill using the swiss-qr-bill package
- Write and compile a letter based on a LaTex template and add the qr bill to the bottom.
- Store the generated pdfs locally.

## Note:
For privacy reasons two directories are not commited to this repositoriy:
- templates folder: containing .tex files as well as logos and other images used to generate the pdf
- config folder: containing a list of known creditors and debtors as well as paths used
