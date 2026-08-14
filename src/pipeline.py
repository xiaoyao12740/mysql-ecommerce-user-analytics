from __future__ import annotations
import argparse,time
from pathlib import Path
from src.data.generate_data import generate
from src.data.validate_data import validate
from src.database.load_data import load
from src.export.export_results import export
from src.visualization.make_figures import figures
ROOT=Path(__file__).resolve().parents[1]
def stage(name,fn):
 t=time.perf_counter(); print(f"[START] {name}"); out=fn(); print(f"[DONE ] {name} ({time.perf_counter()-t:.2f}s)"); return out
def main():
 p=argparse.ArgumentParser(); p.add_argument('--users',type=int,default=50000); p.add_argument('--seed',type=int,default=42); a=p.parse_args()
 stage('Generate data',lambda:generate(a.users,a.seed)); stage('Validate CSV',validate); stage('Create and load MySQL',load); stage('Export SQL results',export); stage('Generate figures',figures); print('Pipeline complete.')
if __name__=='__main__': main()

