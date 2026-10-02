#!/usr/bin/env python3
"""Validates the Tendwell synthetic test data set and the Postman collection.

Usage (from the repo root):  python3 06-quality/test-data/validate_test_data.py
Exit code 0 when every check passes; 1 otherwise. Standard library only.

Checks: CSV parsing and unique keys, foreign keys and same-tenant references, visit status
invariants, server-side distance recomputation, credential status as of the data date,
dose windows, vital out-of-range flags (BR-034), expected payroll and billing totals,
anonymization formats, Postman v2.1 structure, endpoint conformance and fixture equality.
"""
import csv, json, math, os, re, sys
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
API = os.path.join(os.path.dirname(HERE), 'api-tests', 'tendwell.postman_collection.json')
AS_OF_DATE = date(2026, 9, 15)
errors, checks = [], [0]

def check(cond, msg):
    checks[0] += 1
    if not cond:
        errors.append(msg)

def load(name, key):
    with open(os.path.join(HERE, name), newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if key:
        ids = [r[key] for r in rows]
        dup = {i for i in ids if ids.count(i) > 1}
        check(not dup, f'{name}: duplicate {key} {sorted(dup)}')
        return rows, {r[key]: r for r in rows}
    return rows, None

tenants, T = load('tenants.csv', 'tenant_id')
locations, L = load('locations.csv', 'location_id')
users, U = load('users.csv', 'user_id')
caregivers, CG = load('caregivers.csv', 'employee_number')
pay_profiles, PPR = load('pay_profiles.csv', 'pay_profile_id')
credentials, CRD = load('credentials.csv', 'credential_id')
payers, PYR = load('payers.csv', 'payer_id')
clients, CL = load('clients.csv', 'client_number')
auths, SA = load('service_authorizations.csv', 'authorization_id')
holidays, H = load('holidays.csv', 'holiday_id')
periods, PP = load('pay_periods.csv', 'pay_period_id')
visits, VIS = load('visits.csv', 'visit_id')
punches, PCH = load('evv_punches.csv', 'punch_id')
idchecks, IDC = load('identity_checks.csv', 'identity_check_id')
exceptions, EXC = load('visit_exceptions.csv', 'exception_id')
dm, _ = load('distance_matrix_stub.csv', None)
orders, MO = load('medication_orders.csv', 'order_id')
doses, DT = load('dose_tasks.csv', 'dose_task_id')
prns, PRN = load('prn_administrations.csv', 'prn_id')
ranges, VRG = load('vital_ranges.csv', 'vital_range_id')
vitals, VR = load('vital_readings.csv', 'vital_reading_id')
exp_pay, _ = load('expected_payroll_E-2041_2026-09-07.csv', None)
exp_bill, _ = load('expected_billing_C-10234_2026-09.csv', None)
with open(os.path.join(HERE, 'api-fixtures.json'), encoding='utf-8') as f:
    FX = json.load(f)

def ten_of(kind, key):
    return {'U': U, 'E': CG, 'C': CL, 'PYR': PYR, 'LOC': L}[kind][key]['tenant_id']

# ---------- anonymization formats (BRIEF section 2)
for r in users + clients:
    check(re.fullmatch(r'\+1-614-555-01\d\d', r['phone']) is not None, f"{r.get('user_id') or r['client_number']}: phone {r['phone']} outside 555-01xx")
for r in users:
    check(re.fullmatch(r'[a-z.]+@example\.(com|org)', r['email']) is not None, f"{r['user_id']}: email {r['email']}")
for r in clients:
    check(r['medicaid_id'] == '' or re.fullmatch(r'ZZ\d{8}', r['medicaid_id']) is not None, f"{r['client_number']}: Medicaid ID {r['medicaid_id']}")
    check(r['service_address'].endswith('Lakemont, OH 43999'), f"{r['client_number']}: address not in Lakemont, OH 43999")
for r in locations + [dict(address=t['registered_address']) for t in tenants]:
    check(r['address'].endswith('Lakemont, OH 43999'), f"address {r['address']}")

# ---------- tenants, locations, users
for l in locations:
    check(l['tenant_id'] in T, f"{l['location_id']}: tenant {l['tenant_id']}")
for u in users:
    plat = u['roles'].startswith('PLT')
    check((u['tenant_id'] == '') == plat, f"{u['user_id']}: platform users have no tenant; tenant users must")
    if u['tenant_id']:
        check(u['tenant_id'] in T, f"{u['user_id']}: tenant")
        for loc in filter(None, u['locations'].split(';')):
            check(loc in L and L[loc]['tenant_id'] == u['tenant_id'], f"{u['user_id']}: location {loc} not in its tenant")
    check(u['status'] in ('Invited', 'Active', 'Locked', 'Deactivated'), f"{u['user_id']}: status")
    for role in u['roles'].split(';'):
        check(role in ('PLT-ADM', 'PLT-SUP', 'AG-ADM', 'AG-COORD', 'AG-SUPV', 'AG-FIN', 'CG'), f"{u['user_id']}: role {role}")
    if any(r in u['roles'] for r in ('AG-ADM', 'AG-SUPV', 'AG-FIN', 'PLT-')) and u['status'] == 'Active':
        check(u['mfa_method'] in ('TOTP', 'SMS'), f"{u['user_id']}: MFA mandatory role without MFA (BR-006)")

# ---------- caregivers, pay profiles, credentials
for c in caregivers:
    u = U.get(c['user_id'])
    check(u is not None and u['roles'] == 'CG' and u['tenant_id'] == c['tenant_id'], f"{c['employee_number']}: user link")
    check(u and (u['first_name'], u['last_name'], u['email'], u['phone']) == (c['first_name'], c['last_name'], c['email'], c['phone']), f"{c['employee_number']}: name/contact differs from users.csv")
    check((c['status'] == 'Inactive') == (u and u['status'] == 'Deactivated'), f"{c['employee_number']}: caregiver/user status mismatch")
by_cg = {}
for p in pay_profiles:
    check(p['employee_number'] in CG, f"{p['pay_profile_id']}: caregiver")
    by_cg.setdefault(p['employee_number'], []).append(p)
for e, ps in by_cg.items():
    ps.sort(key=lambda p: p['effective_from'])
    for a, b in zip(ps, ps[1:]):
        check(a['effective_to'] and date.fromisoformat(a['effective_to']) + timedelta(days=1) == date.fromisoformat(b['effective_from']), f"{e}: pay profiles overlap or leave a gap")
check(set(by_cg) == set(CG), 'every caregiver needs a pay profile')
for c in credentials:
    check(c['employee_number'] in CG and CG[c['employee_number']]['tenant_id'] == c['tenant_id'], f"{c['credential_id']}: caregiver/tenant")
    days = (date.fromisoformat(c['expires_on']) - AS_OF_DATE).days
    st = 'Expired' if days < 0 else 'Expiring' if days <= 30 else 'Valid'
    check(int(c['days_to_expiry_2026_09_15']) == days and c['status_2026_09_15'] == st, f"{c['credential_id']}: status should be {st} ({days} days)")
    check(c['reminder_due_2026_09_15'] == ({30: '30', 14: '14', 1: '1'}.get(days, '')), f"{c['credential_id']}: reminder flag")

# ---------- payers, clients, authorizations
for p in payers:
    check(p['tenant_id'] in T, f"{p['payer_id']}: tenant")
for c in clients:
    check(c['tenant_id'] in T and L[c['location_id']]['tenant_id'] == c['tenant_id'], f"{c['client_number']}: location/tenant")
    check(re.fullmatch(r'C-\d{5}', c['client_number']) is not None, f"{c['client_number']}: format")
    check(50 <= int(c['geofence_radius_m']) <= 500, f"{c['client_number']}: radius outside 50-500 m (BR-021)")
    for k in ('preferred_caregiver', 'excluded_caregiver'):
        if c[k]:
            check(c[k] in CG and CG[c[k]]['tenant_id'] == c['tenant_id'], f"{c['client_number']}: {k} {c[k]}")
    check(bool(c['excluded_caregiver']) == bool(c['exclusion_reason']), f"{c['client_number']}: exclusion needs a reason")
    check((c['status'] == 'Discharged') == bool(c['discharged_on']), f"{c['client_number']}: discharge fields")
    if c['discharged_on']:
        d = date.fromisoformat(c['discharged_on'])
        check(c['retain_until'] == d.replace(year=d.year + 7).isoformat(), f"{c['client_number']}: retention 7 years (BR-013)")
models = {'Hourly': 'Unit15Min', 'PerVisit': 'Visit', 'Daily': 'Day', 'FixedMonthly': 'Month'}
for a in auths:
    c = CL.get(a['client_number'])
    check(c is not None and c['seed_mode'] == 'loaded', f"{a['authorization_id']}: client")
    check(PYR[a['payer_id']]['tenant_id'] == c['tenant_id'], f"{a['authorization_id']}: payer tenant")
    check(models[a['billing_model']] == a['unit_type'], f"{a['authorization_id']}: unit type vs billing model")
    check(a['period_end'] >= a['period_start'], f"{a['authorization_id']}: period")
    check(a['service_line'] in T[c['tenant_id']]['service_lines'].split(';'), f"{a['authorization_id']}: service line not offered by tenant")
# no overlapping Active authorizations for the same client, payer and code within one seed scenario (US-013-AC4)
for a in auths:
    for b in auths:
        if a is b or a['status'] != 'Active' or b['status'] != 'Active': continue
        if (a['client_number'], a['payer_id'], a['service_code']) == (b['client_number'], b['payer_id'], b['service_code']) and a['seed_scenario'] == b['seed_scenario']:
            check(a['period_end'] < b['period_start'] or b['period_end'] < a['period_start'], f"{a['authorization_id']}/{b['authorization_id']}: overlapping authorizations")
for h in holidays:
    check(h['tenant_id'] in T, f"{h['holiday_id']}: tenant")
for p in periods:
    check(T[p['tenant_id']]['pay_frequency'] == p['frequency'], f"{p['pay_period_id']}: frequency differs from tenant")
    check((p['status'] == 'Locked') == bool(p['locked_at']), f"{p['pay_period_id']}: lock fields")

# ---------- visits
statuses = {'Scheduled', 'InProgress', 'Completed', 'NeedsReview', 'Verified', 'Cancelled', 'Missed'}
check({v['status'] for v in visits} == statuses, 'visits.csv must cover all seven statuses')
for v in visits:
    vid = v['visit_id']; c = CL[v['client_number']]; a = SA[v['service_authorization_id']]
    check(c['tenant_id'] == v['tenant_id'] and c['seed_mode'] == 'loaded', f"{vid}: client tenant")
    check(a['client_number'] == v['client_number'] and a['service_line'] == v['service_line'], f"{vid}: authorization does not match client/service line (BR-009)")
    if v['caregiver']:
        check(CG[v['caregiver']]['tenant_id'] == v['tenant_id'], f"{vid}: caregiver tenant")
        check(v['caregiver'] != c['excluded_caregiver'], f"{vid}: excluded caregiver assigned (BR-017)")
    check((v['is_open_shift'] == 'Y') == (v['caregiver'] == ''), f"{vid}: open shift iff no caregiver")
    st = v['status']; has_s, has_e = bool(v['actual_start']), bool(v['actual_end'])
    exp = {'Scheduled': (False, False), 'Cancelled': (False, False), 'Missed': (False, False), 'InProgress': (True, False)}.get(st, (True, True))
    check((has_s, has_e) == exp, f"{vid}: actual times inconsistent with {st}")
    check(bool(v['cancel_reason']) == (st == 'Cancelled'), f"{vid}: cancel reason")
    check(v['scheduled_end'] > v['scheduled_start'], f"{vid}: schedule")
# overlap check per caregiver (BR-016) on scheduled times for non-cancelled visits
by = {}
for v in visits:
    if v['caregiver'] and v['status'] != 'Cancelled':
        by.setdefault(v['caregiver'], []).append(v)
for e, vs in by.items():
    vs.sort(key=lambda v: datetime.fromisoformat(v['actual_start'] or v['scheduled_start']))
    for a, b in zip(vs, vs[1:]):
        a_end = datetime.fromisoformat(a['actual_end'] or a['scheduled_end'])
        b_start = datetime.fromisoformat(b['actual_start'] or b['scheduled_start'])
        check(a_end <= b_start, f"{e}: {a['visit_id']} overlaps {b['visit_id']}")

# ---------- punches, identity checks, exceptions
R = 6371008.8
def hav(lat1, lng1, lat2, lng2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
for p in punches:
    v = VIS.get(p['visit_id']); check(v is not None, f"{p['punch_id']}: visit")
    c = CL[v['client_number']]
    check(p['source'] in ('Mobile', 'MobileOffline', 'Manual', 'System') and p['type'] in ('In', 'Out'), f"{p['punch_id']}: enums")
    if p['lat'] != '' and p['distance_m'] != '':
        d = round(hav(float(c['lat']), float(c['lng']), float(p['lat']), float(p['lng'])), 1)
        check(f'{d:.1f}' == p['distance_m'], f"{p['punch_id']}: distance {p['distance_m']} but server computes {d:.1f}")
    if p['source'] == 'Manual':
        check(p['reason_code'] and p['note'] and U[p['created_by']]['roles'] == 'AG-COORD', f"{p['punch_id']}: manual punch needs reason, note and a coordinator (BR-026)")
    if p['supersedes_punch_id']:
        sp = PCH.get(p['supersedes_punch_id'])
        check(sp is not None and sp['visit_id'] == p['visit_id'] and sp['type'] == p['type'], f"{p['punch_id']}: supersedes")
    if p['identity_check_id']:
        ic = IDC.get(p['identity_check_id'])
        check(ic is not None and ic['visit_id'] == p['visit_id'] and ic['consumed_by_punch'] == p['punch_id'], f"{p['punch_id']}: identity check link")
        dt = (datetime.fromisoformat(ic['consumed_at']) - datetime.fromisoformat(ic['created_at'])).total_seconds()
        check(0 <= dt <= 90, f"{p['punch_id']}: identity check used after {dt} s (BR-024)")
    if v['tenant_id'] == 'TEN-001' and p['source'] == 'Mobile':
        check(bool(p['identity_check_id']), f"{p['punch_id']}: TEN-001 has identity verification On")
    if p['source'] == 'MobileOffline':
        lag = (datetime.fromisoformat(p['received_at']) - datetime.fromisoformat(p['punch_time'])).total_seconds()
        late = lag > 24 * 3600
        check(late == p['expected_exception'].startswith('LATE_OFFLINE_SYNC') or (late and 'late as well' in p['expected_exception']), f"{p['punch_id']}: late-sync expectation ({lag / 3600:.3f} h)")
used = [ic['consumed_by_punch'] for ic in idchecks]
check(len(used) == len(set(used)), 'an identity check was consumed twice (BR-024)')
for e in exceptions:
    check(e['visit_id'] in VIS, f"{e['exception_id']}: visit")
    check((e['status'] == 'Resolved') == bool(e['resolved_by']), f"{e['exception_id']}: resolution fields")
open_by_visit = {}
for e in exceptions:
    if e['status'] == 'Open':
        open_by_visit.setdefault(e['visit_id'], []).append(e['code'])
for v in visits:
    if v['status'] == 'NeedsReview':
        check(v['visit_id'] in open_by_visit, f"{v['visit_id']}: Needs review without an open exception")
    if v['status'] == 'Verified':
        check(v['visit_id'] not in open_by_visit, f"{v['visit_id']}: Verified with an open exception (FR-EVV-10)")
for row in dm:
    for k in ('from_client', 'to_client'):
        check(row[k] in CL, f"distance stub client {row[k]}")

# ---------- eMAR and vitals
for o in orders:
    check(o['client_number'] in CL, f"{o['order_id']}: client")
    if o['is_prn'] == 'N':
        check(15 <= int(o['window_minutes']) <= 120, f"{o['order_id']}: window outside 15-120 (BR-029)")
    else:
        check(o['prn_indication'] and o['prn_max_per_24h'] and o['prn_min_interval_min'], f"{o['order_id']}: PRN fields")
    check((o['status'] == 'PendingApproval') == (o['approved_by'] == ''), f"{o['order_id']}: approval fields")
    if o['approved_by']:
        check('AG-SUPV' in U[o['approved_by']]['roles'], f"{o['order_id']}: approver must be AG-SUPV (FR-MAR-01)")
for d in doses:
    o = MO[d['order_id']]
    check(o['status'] == 'Active' and o['is_prn'] == 'N', f"{d['dose_task_id']}: dose tasks only for Active scheduled orders")
    check(d['client_number'] == o['client_number'], f"{d['dose_task_id']}: client")
    s = datetime.fromisoformat(d['scheduled_at']); w = timedelta(minutes=int(o['window_minutes']))
    check(datetime.fromisoformat(d['window_start']) == s - w and datetime.fromisoformat(d['window_end']) == s + w, f"{d['dose_task_id']}: window")
    check(datetime.fromisoformat(d['missed_at']) == s + w + timedelta(minutes=60), f"{d['dose_task_id']}: missed threshold")
    if d['status'] in ('Refused', 'Held', 'NotAvailable'):
        check(bool(d['reason']), f"{d['dose_task_id']}: reason required (BR-032)")
    if d['is_late_entry'] == 'Y':
        check(datetime.fromisoformat(d['recorded_at']) > datetime.fromisoformat(d['window_end']), f"{d['dose_task_id']}: late entry recorded inside window")
for p in prns:
    check(MO[p['order_id']]['is_prn'] == 'Y' and p['indication'], f"{p['prn_id']}: PRN order and indication (BR-033)")
for o in orders:
    if o['is_prn'] == 'Y':
        times = sorted(datetime.fromisoformat(p['administered_at']) for p in prns if p['order_id'] == o['order_id'])
        for a, b in zip(times, times[1:]):
            check((b - a).total_seconds() / 60 >= int(o['prn_min_interval_min']), f"{o['order_id']}: seeded PRN doses violate the interval")
        for t in times:
            n = sum(1 for x in times if t - timedelta(hours=24) < x <= t)
            check(n <= int(o['prn_max_per_24h']), f"{o['order_id']}: seeded PRN doses exceed the 24 h maximum")
ov = {(r['client_number'], r['type']): r for r in ranges}
for r in vitals:
    v = VIS[r['visit_id']]
    check(v['client_number'] == r['client_number'] and r['recorded_by'] == v['caregiver'], f"{r['vital_reading_id']}: visit/client/recorder")
    v1 = float(r['value_1']); v2 = float(r['value_2']) if r['value_2'] else None; c = r['client_number']; t = r['type']
    if t == 'BP': o = v1 < 90 or v1 > 180 or (v2 is not None and v2 > 110)
    elif t == 'PULSE': o = v1 < 50 or v1 > 120
    elif t == 'TEMP': o = v1 >= 100.4
    elif t == 'SPO2': o = v1 < float(ov[(c, 'SPO2')]['low']) if (c, 'SPO2') in ov else v1 < 92
    elif t == 'GLUCOSE':
        lo, hi = (float(ov[(c, 'GLUCOSE')]['low']), float(ov[(c, 'GLUCOSE')]['high'])) if (c, 'GLUCOSE') in ov else (70, 300)
        o = v1 < lo or v1 > hi
    else: o = False
    check(r['expected_out_of_range'] == ('Y' if o else 'N'), f"{r['vital_reading_id']}: out-of-range flag (BR-034)")

# ---------- expected outputs
wages = sum(int(r['amount_cents']) for r in exp_pay if r['is_wages'] == 'Y')
reimb = sum(int(r['amount_cents']) for r in exp_pay if r['is_wages'] == 'N')
hours = sum(float(r['quantity']) for r in exp_pay if r['quantity_unit'] == 'Hours')
for r in exp_pay:
    check(round(float(r['quantity']) * int(r['rate_cents'])) == int(r['amount_cents']), f"payroll line {r['line_type']}: quantity x rate")
    for vid in r['source_visit_ids'].split(';'):
        check(VIS[vid]['caregiver'] == 'E-2041' and VIS[vid]['status'] == 'Verified', f"payroll source {vid}")
check((wages, reimb, wages + reimb, hours) == (92625, 3234, 95859, 43.0), f'payroll totals {wages}/{reimb}/{hours}')
for scen, total, billable, nonbill in (('base', 17400, 24, 0), ('auth-cap', 14500, 20, 4)):
    lines = [r for r in exp_bill if r['scenario'] == scen and r['line_kind'] == 'Line']
    tot = [r for r in exp_bill if r['scenario'] == scen and r['line_kind'] == 'Total'][0]
    check(sum(int(r['amount_cents']) for r in lines if r['billable'] == 'Y') == int(tot['amount_cents']) == total, f'billing {scen} amount')
    check(sum(int(r['units']) for r in lines if r['billable'] == 'Y') == int(tot['units']) == billable, f'billing {scen} units')
    check(sum(int(r['units']) for r in lines if r['billable'] == 'N') == nonbill, f'billing {scen} not-billable units')
    for r in lines:
        if r['verified_minutes']:
            v = VIS[r['visit_id']]
            m = int((datetime.fromisoformat(v['actual_end']) - datetime.fromisoformat(v['actual_start'])).total_seconds() // 60)
            check(m == int(r['verified_minutes']), f"billing {r['visit_id']}: minutes")

# ---------- Postman collection (v2.1 structure, endpoints, fixtures)
ENDPOINTS = '''POST /auth/login|POST /auth/mfa/verify|POST /auth/refresh|POST /auth/logout|POST /auth/password/forgot|POST /auth/password/reset|GET /plans|POST /promo-codes/validate|POST /signups|POST /signups/{}/verify-email|GET /subscription|PATCH /subscription|GET /users|POST /users|PATCH /users/{}|PUT /users/{}/roles|PUT /users/{}/permission-overrides|GET /users/{}/effective-permissions|POST /support-access-grants|POST /support-access-grants/{}/approve|POST /support-access-grants/{}/revoke|GET /clients|POST /clients|GET /clients/{}|PATCH /clients/{}|POST /clients/{}/phi-reveals|POST /clients/{}/discharge|GET /clients/{}/authorizations|POST /clients/{}/authorizations|POST /clients/{}/care-plans|POST /care-plans/{}/approve|GET /caregivers|POST /caregivers|PATCH /caregivers/{}|POST /caregivers/{}/deactivate|POST /caregivers/{}/credentials|GET /credentials|PUT /caregivers/{}/pay-profiles|POST /visit-patterns|GET /visits|POST /visits|PATCH /visits/{}|POST /visits/{}/cancel|POST /visits/compliance-checks|GET /open-shifts|POST /visits/{}/claim|POST /visits/{}/identity-checks|POST /visits/{}/clock-in|POST /visits/{}/clock-out|POST /evv/punches/sync|GET /visit-exceptions|POST /visit-exceptions/{}/resolve|POST /visits/{}/time-corrections|POST /clients/{}/medication-orders|POST /medication-orders/{}/approve|POST /medication-orders/{}/discontinue|GET /dose-tasks|POST /dose-tasks/{}/outcome|POST /medication-orders/{}/prn-administrations|POST /clients/{}/vital-readings|PUT /clients/{}/vital-ranges|GET /clients/{}/mar|GET /pay-periods|GET /pay-periods/{}/summary|GET /pay-periods/{}/pre-export-review|POST /pay-periods/{}/exports|POST /billing-runs|GET /invoices|GET /invoices/{}|POST /invoices/{}/approve|POST /invoices/{}/issue|POST /invoices/{}/void|POST /invoices/{}/payment-links|POST /invoices/{}/credit-notes|POST /claim-batches|GET /audit-events|POST /audit-events/exports'''.split('|')
EP = [(e.split(' ')[0], re.compile('^' + re.escape(e.split(' ')[1]).replace(r'\{\}', r'[^/]+') + '$')) for e in ENDPOINTS]
with open(API, encoding='utf-8') as f:
    PM = json.load(f)
check(PM['info']['schema'] == 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json', 'Postman info.schema')
check(bool(PM['info'].get('name')) and isinstance(PM.get('item'), list), 'Postman info.name and item[]')
defined = {v['key'] for v in PM.get('variable', [])}
for v in PM['variable']:
    check(set(v) >= {'key', 'value'}, f"variable {v}")
check({'baseUrl', 'accessToken', 'tenantBAccessToken'} <= defined, 'required collection variables')
check(any(v['key'] == 'baseUrl' and v['value'] == 'https://api.tendwell.example/v1' for v in PM['variable']), 'baseUrl value')
pre = ' '.join(PM['event'][0]['script']['exec'])
check(PM['event'][0]['listen'] == 'prerequest' and 'Idempotency-Key' in pre and 'uuid' in pre, 'collection pre-request sets Idempotency-Key')
fixture_bodies = []
def walk(o):
    if isinstance(o, dict):
        fixture_bodies.append(o)
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
walk({k: v for k, v in FX.items() if k not in ('_meta', 'engineCases')})
folder_names = [f['name'] for f in PM['item']]
check(folder_names == ['Auth', 'Clients', 'Scheduling', 'EVV', 'eMAR', 'Payroll', 'Billing', 'Security'], f'Postman folders {folder_names}')
n_req = 0
for folder in PM['item']:
    check('item' in folder and 'request' not in folder, f"folder {folder['name']} shape")
    for it in folder['item']:
        n_req += 1
        r = it['request']
        check(r['method'] in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'), f"{it['name']}: method")
        raw = r['url']['raw']
        check(raw.startswith('{{baseUrl}}/'), f"{it['name']}: url must start with {{baseUrl}}")
        path = '/' + '/'.join(r['url']['path'])
        path = re.sub(r'\{\{[^}]+\}\}', 'x', path)
        check(any(m == r['method'] and rx.match(path) for m, rx in EP), f"{it['name']}: {r['method']} {path} is not a BRIEF section 8 endpoint")
        check(raw.split('?')[0].replace('{{baseUrl}}', '') == '/' + '/'.join(r['url']['path']), f"{it['name']}: url.raw and url.path differ")
        used_vars = set(re.findall(r'\{\{([^}]+)\}\}', json.dumps(it)))
        check(used_vars <= defined, f"{it['name']}: undefined variables {used_vars - defined}")
        tests = [e for e in it['event'] if e['listen'] == 'test']
        check(tests and any('pm.test(' in line for line in tests[0]['script']['exec']), f"{it['name']}: needs pm.test assertions")
        check(any('to.have.status' in line for line in tests[0]['script']['exec']), f"{it['name']}: needs a status assertion")
        if 'body' in r:
            body = json.loads(r['body']['raw'])
            check(body in fixture_bodies, f"{it['name']}: body not taken from api-fixtures.json")
        auth = r.get('auth', PM['auth'])
        check(auth['type'] in ('bearer', 'noauth'), f"{it['name']}: auth")
check(20 <= n_req <= 32, f'Postman request count {n_req}')
# deterministic UUID variables must point at existing records
PFX = {'7e000000': T, 'c1000000': CL, 'ca000000': CG, 'd0000000': VIS, 'd0500000': DT, '3e000000': MO, '9a000000': PP}
for v in PM['variable']:
    m = re.fullmatch(r'([0-9a-f]{8})-0000-4000-8000-(\d{12})', v['value'])
    if m:
        table = PFX[m.group(1)]
        check(any(re.sub(r'\D', '', k.split('-', 1)[1].replace('T', '9')).lstrip('0') == m.group(2).lstrip('0') for k in table), f"variable {v['key']}: no record for {v['value']}")

print(f'{checks[0]} checks, {len(errors)} failures')
for e in errors:
    print('FAIL', e)
print(f'rows: tenants {len(tenants)}, users {len(users)}, caregivers {len(caregivers)}, clients {len(clients)}, authorizations {len(auths)}, '
      f'visits {len(visits)}, punches {len(punches)}, dose tasks {len(doses)}, vitals {len(vitals)}; Postman requests {n_req}')
sys.exit(1 if errors else 0)
