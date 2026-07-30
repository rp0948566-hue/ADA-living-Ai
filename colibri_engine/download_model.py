"""One-shot, resumable download of the GLM-5.2 colibri int4 model (~430 GB)
to C:\\colibri_models\\glm52_i4. Meant to run detached/in the background —
huggingface_hub's snapshot_download resumes automatically if interrupted,
so this is safe to just re-run if it ever gets killed partway through.
"""
from huggingface_hub import snapshot_download

if __name__ == "__main__":
    path = snapshot_download(
        repo_id="mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp",
        local_dir=r"C:\colibri_models\glm52_i4",
        max_workers=4,
    )
    print(f"DOWNLOAD_COMPLETE: {path}", flush=True)
