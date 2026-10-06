CREATE EXTENSION IF NOT EXISTS timescaledb;
-- ORM definitions live in apps/api/app/models.py.
-- Production migrations should create hypertables on:
-- rank_measurements(observed_at), cwv_measurements(observed_at), gsc_measurements(observed_at).
