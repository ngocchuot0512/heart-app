-- Chạy trong Supabase > SQL Editor.
-- Bảng lịch sử đánh giá (tương thích bản cũ: các cột mới đều cho phép NULL).
create table if not exists public.diagnosis_history (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  patient_name text,
  age int,
  sex text,
  trestbps int,
  chol int,
  prediction_result text,
  risk_probability numeric
);

-- Cột bổ sung cho bản nâng cấp (nếu bảng cũ đã tồn tại, các lệnh này sẽ thêm cột còn thiếu).
alter table public.diagnosis_history
  add column if not exists risk_level text,
  add column if not exists height_cm numeric,
  add column if not exists weight_kg numeric,
  add column if not exists bmi numeric,
  add column if not exists systolic int,
  add column if not exists diastolic int,
  add column if not exists smoking text,
  add column if not exists activity text,
  add column if not exists cardio_history text,
  add column if not exists thalach int,
  add column if not exists oldpeak numeric,
  add column if not exists inputs jsonb;   -- toàn bộ 13 chỉ số đưa vào mô hình

-- Hồ sơ cá nhân
create table if not exists public.profiles (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  full_name text,
  birth_year int,
  sex text,
  updated_at timestamptz default now()
);

-- Row Level Security: mỗi người chỉ thấy / sửa dữ liệu của chính mình.
alter table public.diagnosis_history enable row level security;
alter table public.profiles enable row level security;

drop policy if exists "history_select_own" on public.diagnosis_history;
drop policy if exists "history_insert_own" on public.diagnosis_history;
drop policy if exists "history_delete_own" on public.diagnosis_history;
create policy "history_select_own" on public.diagnosis_history for select using (auth.uid() = user_id);
create policy "history_insert_own" on public.diagnosis_history for insert with check (auth.uid() = user_id);
create policy "history_delete_own" on public.diagnosis_history for delete using (auth.uid() = user_id);

drop policy if exists "profiles_all_own" on public.profiles;
create policy "profiles_all_own" on public.profiles for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
