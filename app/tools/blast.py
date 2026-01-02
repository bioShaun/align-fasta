import subprocess
import json
import os
from typing import List, Dict, Any
from .base import AlignmentTool

class BlastTool(AlignmentTool):
    def index(self, fasta_path: str, output_path: str) -> bool:
        """Runs makeblastdb."""
        # Determine dbtype (nucl or prot)
        # For simplicity, we assume nucl for now
        cmd = [
            "makeblastdb",
            "-in", fasta_path,
            "-dbtype", "nucl",
            "-out", output_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search(self, query_path: str, db_path: str, options: Dict[str, Any]) -> str:
        """Runs blastn and returns the path to the JSON output."""
        program = options.get("program", "blastn")
        output_path = query_path + ".blast.json"
        
        cmd = [
            program,
            "-query", query_path,
            "-db", db_path,
            "-outfmt", "15",
            "-out", output_path
        ]
        
        # Add optional parameters
        if "evalue" in options:
            cmd.extend(["-evalue", str(options["evalue"])])
        
        # Always set task parameter, default to blastn
        task = options.get("task", "blastn")
        cmd.extend(["-task", str(task)])
            
        print(f"DEBUG: Running BLAST command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return output_path

    def parse_result(self, result_path: str) -> List[Dict[str, Any]]:
        """Parses BLAST JSON output."""
        if not os.path.exists(result_path):
            return []
            
        with open(result_path, 'r') as f:
            data = json.load(f)
            
        hits = []
        try:
            blast_outputs = data.get("BlastOutput2", [])
            for output in blast_outputs:
                search_results = output.get("report", {}).get("results", {}).get("search", {})
                query_title = search_results.get("query_title", "Unknown")
                query_len = search_results.get("query_len", 0)
                hits_raw = search_results.get("hits", [])
                for h in hits_raw:
                    description = h.get("description", [{}])[0]
                    hsps = h.get("hsps", [{}])
                    for hsp in hsps:
                        align_len = hsp.get("align_len", 0)
                        identity = hsp.get("identity", 0)
                        gaps = hsp.get("gaps", 0)
                        # Calculate pident (percentage identity)
                        pident = round((identity / align_len * 100), 2) if align_len > 0 else 0
                        # Calculate mismatch = align_len - identity - gaps
                        mismatch = align_len - identity - gaps if align_len > 0 else 0
                        
                        hits.append({
                            # outfmt 6 standard columns
                            "qseqid": query_title,
                            "sseqid": description.get("accession", ""),
                            "pident": pident,
                            "length": align_len,
                            "mismatch": mismatch,
                            "gapopen": gaps,
                            "qstart": hsp.get("query_from"),
                            "qend": hsp.get("query_to"),
                            "sstart": hsp.get("hit_from"),
                            "send": hsp.get("hit_to"),
                            "evalue": hsp.get("evalue"),
                            "bitscore": hsp.get("bit_score"),
                            # Extra fields for display
                            "stitle": description.get("title", ""),
                            "qlen": query_len,
                        })
        except (KeyError, IndexError):
            pass
            
        return hits
