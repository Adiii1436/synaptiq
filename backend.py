import os
import shutil
import time
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QThread, Signal
import worker as backend

class OrganizerWorker(QThread):
    # Signals to update UI
    log_signal = Signal(str)
    progress_signal = Signal(float)
    stats_signal = Signal(int, int, int) # total, processed, groups
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, path_str, mode):
        super().__init__()
        self.path_str = path_str
        self.mode = mode
        self.is_running = True

    def log(self, msg):
        self.log_signal.emit(msg)

    def run(self):
        """Main Thread Execution Entry Point"""
        try:
            path = Path(self.path_str)
            files = backend.scan_files(self.path_str)
            total_files = len(files)
            
            if total_files == 0:
                self.error_signal.emit("No files found in directory.")
                return

            self.stats_signal.emit(total_files, 0, 0)
            self.log(f"Found {total_files} files. Mode: '{self.mode}'")

            if self.mode == "type":
                self._process_type(path, files)
            elif self.mode == "date":
                self._process_date(path, files)
            elif self.mode == "ai":
                self._process_ai(path, files)
            
            self.log("✅ Task Completed.")
            self.finished_signal.emit()

        except Exception as e:
            self.error_signal.emit(f"Critical Error: {str(e)}")

    def stop(self):
        self.is_running = False

    # --- MODE 1: FILE TYPE ---
    def _process_type(self, path, files):
        groups = set()
        for i, f in enumerate(files):
            if not self.is_running: break
            try:
                ext = f.suffix.lower().strip('.') or "no_extension"
                target = path / ext
                target.mkdir(exist_ok=True)
                
                self._safe_move(f, target)
                groups.add(ext)
                
                self._update_progress(i + 1, len(files), len(groups))
            except Exception as e:
                self.log(f"Error: {e}")

    # --- MODE 2: DATE ---
    def _process_date(self, path, files):
        groups = set()
        for i, f in enumerate(files):
            if not self.is_running: break
            try:
                ts = os.path.getmtime(f)
                folder = datetime.fromtimestamp(ts).strftime("%Y-%m")
                target = path / folder
                target.mkdir(exist_ok=True)
                
                self._safe_move(f, target)
                groups.add(folder)
                
                self._update_progress(i + 1, len(files), len(groups))
            except Exception as e:
                self.log(f"Error: {e}")

    # --- MODE 3: AI CLUSTERING ---
    def _process_ai(self, path, files):
        # 1. Check/Download Models
        is_ready, missing = backend.check_local_model_ready()
        if not is_ready:
            self.log(f"⚠️ Missing Chat Model: {missing[0]}")
            for status in backend.download_local_model(missing[0]):
                if not self.is_running: return
                self.log(status)
        
        total = len(files)
        ai_candidates = []  
        processed_count = 0
        groups_created = set()

        # 2. Hardcoded Phase (Fast)
        self.log("📦 Phase 1: Sorting Binaries & Media...")
        
        media_map = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
            'Videos': ['.mp4', '.mkv', '.mov', '.avi', '.wmv'],
            'Audio':  ['.mp3', '.wav', '.flac'],
            'Execs':  ['.exe', '.msi', '.bat', '.sh', '.bin', '.iso'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }

        for i, f in enumerate(files):
            if not self.is_running: break
            
            suffix = f.suffix.lower()
            moved = False
            
            for folder, exts in media_map.items():
                if suffix in exts:
                    target = path / folder
                    target.mkdir(exist_ok=True)
                    self._safe_move(f, target)
                    groups_created.add(folder)
                    moved = True
                    break
            
            if moved:
                processed_count += 1
            else:
                ai_candidates.append(f)

            # Update stats (First 10% of progress bar)
            self.progress_signal.emit((i / total) * 0.10)
            self.stats_signal.emit(total, processed_count, len(groups_created))

        if not ai_candidates: return

        # 3. AI Phase (Smart)
        ai_total = len(ai_candidates)
        self.log(f"🧠 Phase 2: AI Processing for {ai_total} documents...")

        # A. Extract Text
        texts = []
        valid_files = []
        
        for i, f in enumerate(ai_candidates):
            if not self.is_running: break
            
            txt = backend.extract_text(f)
            if len(txt) > 10: # Only process if we found text
                texts.append(txt)
                valid_files.append(f)
            else:
                # No text found? Move to misc
                target = path / "Misc_Files"
                target.mkdir(exist_ok=True)
                self._safe_move(f, target)
                processed_count += 1
            
            # Progress 10% -> 40%
            prog = 0.10 + (i / ai_total) * 0.30
            self.progress_signal.emit(prog)

        if not valid_files: return

        # B. Generate Embeddings (Vectorization)
        # Note: We do this one-by-one to keep UI responsive, 
        # but SentenceTransformer is fast enough that it won't matter much.
        self.log("  • Generating Semantic Vectors...")
        embeddings = []
        for i, txt in enumerate(texts):
            if not self.is_running: break
            
            emb = backend.generate_embedding(txt)
            embeddings.append(emb)
            
            # Progress 40% -> 70%
            prog = 0.40 + (i / len(texts)) * 0.30
            self.progress_signal.emit(prog)

        if not self.is_running: return

        # C. Cluster
        self.log("  • Clustering content...")
        labels = backend.cluster_embeddings(embeddings)
        unique_labels = set(labels)
        
        # D. Name & Move
        self.log(f"  • Identified {len(unique_labels)} unique topics.")
        
        # Group files by label
        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters: clusters[label] = []
            clusters[label].append(idx)

        # Process each cluster
        for i, (label, indices) in enumerate(clusters.items()):
            if not self.is_running: break
            
            cluster_files = [valid_files[x] for x in indices]
            cluster_texts = [texts[x] for x in indices]
            
            self.log(f"  • Naming Group {i+1}/{len(clusters)}...")
            folder_name = backend.get_smart_folder_name(cluster_files, cluster_texts)
            
            target_dir = path / folder_name
            target_dir.mkdir(exist_ok=True)
            groups_created.add(folder_name)
            
            for f in cluster_files:
                self._safe_move(f, target_dir)
                processed_count += 1
            
            # Progress 70% -> 100%
            prog = 0.70 + (i / len(clusters)) * 0.30
            self.progress_signal.emit(prog)
            self.stats_signal.emit(total, processed_count, len(groups_created))

    def _safe_move(self, src: Path, dest_dir: Path):
        """Moves file, handling duplicates."""
        dest = dest_dir / src.name
        if dest.exists():
            timestamp = int(time.time())
            dest = dest_dir / f"{src.stem}_{timestamp}{src.suffix}"
        shutil.move(str(src), str(dest))

    def _update_progress(self, current, total, groups):
        self.progress_signal.emit(current / total)
        self.stats_signal.emit(total, current, groups)