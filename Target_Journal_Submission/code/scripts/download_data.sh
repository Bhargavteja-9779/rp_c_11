#!/usr/bin/env bash
# Download public datasets used in the study (no registration required).
#  * UCR Time Series Classification Archive 2018 (Dau et al. 2019), .ts format distributed by timeseriesclassification.com
#  * PhysioNet/Computing in Cardiology Challenge 2012 (Silva et al. 2012), Open Data Commons Attribution License v1.0
#  * CWRU Bearing Data Center (https://engineering.case.edu/bearingdatacenter): 12k drive-end fault + normal baseline files
set -euo pipefail
cd "$(dirname "$0")/../data/raw" 2>/dev/null || { mkdir -p "$(dirname "$0")/../data/raw"; cd "$(dirname "$0")/../data/raw"; }
if [ ! -d Univariate_ts ]; then
  curl -L -o Univariate2018_ts.zip https://www.timeseriesclassification.com/aeon-toolkit/Archives/Univariate2018_ts.zip
  unzip -q Univariate2018_ts.zip
fi
mkdir -p physionet2012 && cd physionet2012
for f in set-a.tar.gz set-b.tar.gz set-c.tar.gz Outcomes-a.txt Outcomes-b.txt Outcomes-c.txt; do
  [ -f "$f" ] || curl -sfL -O "https://physionet.org/files/challenge-2012/1.0.0/$f"
done
for s in a b c; do [ -d "set-$s" ] || tar xzf "set-$s.tar.gz"; done
cd .. && mkdir -p cwru && cd cwru
for f in 97 98 99 100 105 106 107 108 118 119 120 121 130 131 132 133 169 170 171 172 185 186 187 188 197 198 199 200 \
         209 210 211 212 222 223 224 225 234 235 236 237; do
  [ -f "$f.mat" ] || curl -sfL -o "$f.mat" "https://engineering.case.edu/sites/default/files/$f.mat"
done
echo "data ready"
