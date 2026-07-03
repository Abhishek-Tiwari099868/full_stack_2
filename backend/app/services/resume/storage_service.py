import os
from supabase import create_client
import uuid

class SupabaseStorageService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.bucket_name = os.getenv("SUPABASE_BUCKET", "resumes")
        self.client = None
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase storage client: {str(e)}")

    def upload_resume(self, file_data, user_id, original_filename):
        """
        Uploads a resume file stream to Supabase Storage.
        Returns a tuple of (file_path, public_url).
        """
        if not self.client:
            raise ValueError(
                "Supabase Storage client is not configured. "
                "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your environment variables."
            )

        # Generate a unique filename using UUID to prevent collisions
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "pdf"
        unique_filename = f"{uuid.uuid4()}.{ext}"
        path_in_bucket = f"user_{user_id}/{unique_filename}"

        # Read file bytes
        file_bytes = file_data.read()
        file_data.seek(0)  # Reset stream position

        try:
            # Upload the file bytes to Supabase Storage
            # Note: client.storage.from_(bucket).upload handles bytes or file-like objects
            self.client.storage.from_(self.bucket_name).upload(
                path=path_in_bucket,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )
            
            # Get public url
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(path_in_bucket)
            return path_in_bucket, public_url
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to Supabase Storage: {str(e)}")

    def delete_resume(self, path_in_bucket):
        """Deletes a resume file from Supabase Storage."""
        if not self.client:
            return
        try:
            self.client.storage.from_(self.bucket_name).remove([path_in_bucket])
        except Exception as e:
            # Log warning but do not crash the transaction
            print(f"Warning: Failed to delete old resume from Supabase Storage: {str(e)}")
