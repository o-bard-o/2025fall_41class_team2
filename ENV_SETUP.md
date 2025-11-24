# Environment Setup

## Backend Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in the required values in `.env`:
   - `SECRET_KEY`: Django secret key (generate one if needed)
   - `OPENAI_API_KEY`: Your OpenAI API key (required for RAG functionality)
   - Other optional settings as needed

## Frontend Environment Variables

1. Create `frontend/.env.local`:
   ```bash
   cd frontend
   touch .env.local
   ```

2. Add the following variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### Supabase Keys
1. Go to https://supabase.com/
2. Create a new project or select existing one
3. Go to Project Settings > API
4. Copy the Project URL and `anon/public` key
5. Add them to `frontend/.env.local`
