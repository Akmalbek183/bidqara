-- Supabase SQL Editor'da bir marta ishga tushiring
create table if not exists tenders (
  id bigserial primary key,
  source text not null,              -- WB, UNDP, ADB, ...
  external_id text not null,         -- manbadagi noyob ID
  title text not null,
  country text,
  client text,
  method text,                       -- QCBS, CQS, RFQ, RFP...
  deadline date,
  url text,
  raw jsonb,                         -- manbadan kelgan xom ma'lumot
  first_seen timestamptz default now(),
  unique (source, external_id)
);

create table if not exists clients (
  id bigserial primary key,
  name text not null,
  telegram_chat_id text,
  profile jsonb not null,            -- sektorlar, mamlakatlar, tajriba, chegaralar
  min_score int default 60,
  active boolean default true,
  created_at timestamptz default now()
);

create table if not exists assessments (
  id bigserial primary key,
  tender_id bigint references tenders(id) on delete cascade,
  client_id bigint references clients(id) on delete cascade,
  score int,
  verdict text,                      -- GO / REVIEW / SKIP
  summary text,
  criteria jsonb,                    -- [{status:ok|ko|mb, text:...}]
  budget_estimate text,
  notified boolean default false,
  created_at timestamptz default now(),
  unique (tender_id, client_id)
);

-- Birinchi mijoz: o'zingiz. profile'ni o'zgartiring.
insert into clients (name, telegram_chat_id, profile, min_score) values (
  'Global Advisors LLC',
  null,
  '{
    "sectors": ["energy efficiency","buildings","water supply","education infrastructure","agriculture","livestock","social protection","M&E","public investment management","construction supervision","technical inspection"],
    "countries": ["Uzbekistan","Tajikistan","Kyrgyz Republic","Kazakhstan"],
    "firm_type": "local consulting firm, 7 staff + 100 expert roster, est. 2017, Tashkent",
    "experience": "World Bank CEBU project: 4 contracts (technical inspection of buildings, energy audits, school design); sub-consultant to SUNJIN (Korea); JV with Hydroplan (Germany) on water; UNDP/IFAD/IsDB EOIs",
    "annual_turnover_usd": 450000,
    "largest_contract_usd": 180000,
    "ifi_contracts_completed": 9,
    "can_lead_international": false,
    "wants_jv_opportunities": true
  }'::jsonb,
  60
) on conflict do nothing;
