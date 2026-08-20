# CLIgraber By NOVEOP

Hey boys and girls, Iam Nove OP as you all know there are many web crawlers in the internet world, When i first learned about crawlers i got curiosity to make one myself. hmm i know python well so why not ?
and i made this CLIgraber, the name shows a simple thing. CLI means CLI and graber means it grabs items from network world. and thats it, CLIgraber means it grabs things from network using CLI.

# How to Use it ?

you can get the exe file of CLIgraber from our github releases : <br>
https://github.com/NOVE300IQ/CLIgraber/releases 

and instructions are there DW :D

# Usage

Basic usage:

python crawler.py https://example.com

Crawl up to 50 pages:

python crawler.py https://example.com --max-pages 50

Short version:

python crawler.py https://example.com -m 50

Change the delay between requests:

python crawler.py https://example.com -m 50 -d 2

Save the results with a custom name:

python crawler.py https://example.com -o data/example.json

You can also use a website without typing https://:

python crawler.py example.com

See all available options:

python crawler.py --help
