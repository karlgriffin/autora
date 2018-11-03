Installation:
	1) run 'install.bat'
-- end installation--

Configure:
	1) configure 'alias' name - csv header for brand
	2) Add the relevant alias items csv to input folder
	3) configure 'amazon' details within 'config.py'
	4) configure 'google' details within 'config.py'
	5) configure 'input_csv' details within 'config.py'
	6) configure 'folder_name' and 'output_csv' details within 'config.py'
	7) Run 'RUN_PROGRAM.bat'
	8) Once completed, Results are available within the 'reports' folder as an output csv
-- end configure--

Result Logic:
	If Both Amazon and Google return product information add 'Hits' to the result column within the output csv
	If only Amazon or Google have product info add 'Hit' to the result column within the output csv
	If neither Amazon or Goolge have products to return leave results column blanks within the output csv
-- end logic --

QA tested with versions:
	Google Chrome - 68.0.3440.106
	selenium==3.4.3
	beautifulsoup4==4.6.0

-- end readme --