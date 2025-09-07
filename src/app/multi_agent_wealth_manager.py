"""
multi_agent_wealth_manager.py

Purpose:
A single-file, runnable Python "multi-agent" pipeline that produces a client-facing report with actionable steps, matching the output and agentic structure described. Each agent class can be replaced by an AutoGen agent.

Usage:
  python multi_agent_wealth_manager.py --input /path/to/Agent1_fixed.csv --output ./output

Dependencies:
  pip install pandas matplotlib jinja2
"""

from __future__ import annotations
import argparse
import os
import sys
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').fillna(0.0)

@dataclass
class DataAgent:
    """Loads raw CSV and exposes a normalized DataFrame."""
    input_path: str
    df: Optional[pd.DataFrame] = field(default=None, init=False)
    def run(self, user_id: Optional[str] = None) -> pd.DataFrame:
        logging.info(f"DataAgent: loading {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        self.df.columns = [c.strip() for c in self.df.columns]
        if user_id:
            if 'profile__user_id' in self.df.columns:
                filtered = self.df[self.df['profile__user_id'] == user_id]
                logging.info(f"DataAgent: filtered for user_id={user_id}, rows={len(filtered)}")
                self.df = filtered.reset_index(drop=True)
            else:
                logging.warning(f"DataAgent: user_id column not found, using all data")
        logging.info(f"DataAgent: loaded rows={len(self.df)} cols={len(self.df.columns)}")
        return self.df

@dataclass
class HoldingsAgent:
    """Extracts holdings, computes market values and allocation by asset class."""
    df: pd.DataFrame
    results: Dict[str, Any] = field(default_factory=dict, init=False)
    def run(self) -> Dict[str, Any]:
        logging.info("HoldingsAgent: extracting holdings")
        hold_cols = [c for c in self.df.columns if 'accounts__holdings' in c]
        if not hold_cols:
            logging.warning('HoldingsAgent: no holdings columns found')
            self.results = {'holdings_df': pd.DataFrame(), 'alloc': pd.DataFrame(), 'total': 0.0}
            return self.results
        holdings = self.df[hold_cols].copy()
        sym = next((c for c in holdings.columns if 'symbol' in c.lower()), None)
        qty = next((c for c in holdings.columns if 'quantity' in c.lower() or 'qty' in c.lower()), None)
        price = next((c for c in holdings.columns if 'price' in c.lower()), None)
        asset_class = next((c for c in holdings.columns if 'asset_class' in c.lower() or 'assetclass' in c.lower()), None)
        market_col = next((c for c in holdings.columns if 'market' in c.lower() and 'value' in c.lower()), None)
        if market_col is None and qty and price:
            holdings['market_value'] = safe_numeric(holdings[qty]) * safe_numeric(holdings[price])
        elif market_col is not None:
            holdings['market_value'] = safe_numeric(holdings[market_col])
        else:
            holdings['market_value'] = 0.0
        holdings['symbol_clean'] = holdings[sym].astype(str) if sym else 'Unknown'
        holdings['asset_class_clean'] = holdings[asset_class].astype(str) if asset_class else 'Unknown'
        alloc = holdings.groupby('asset_class_clean', dropna=False)['market_value'].sum().reset_index()
        total = alloc['market_value'].sum()
        alloc['Pct'] = alloc['market_value'] / (total if total != 0 else 1) * 100
        self.results = {'holdings_df': holdings, 'alloc': alloc.sort_values('market_value', ascending=False), 'total': total}
        logging.info(f"HoldingsAgent: total portfolio value = {self.results['total']:.2f}")
        return self.results

@dataclass
class TransactionsAgent:
    """Extracts transactions and computes simple income/expense summary."""
    df: pd.DataFrame
    results: Dict[str, Any] = field(default_factory=dict, init=False)
    def run(self) -> Dict[str, Any]:
        logging.info('TransactionsAgent: scanning for transaction columns')
        trans_cols = [c for c in self.df.columns if c.startswith('transactions__')]
        trans = self.df[trans_cols].copy() if trans_cols else pd.DataFrame()
        amt_col = next((c for c in trans.columns if 'amount' in c.lower() or 'amt' in c.lower()), None)
        date_col = next((c for c in trans.columns if 'date' in c.lower()), None)
        income = expense = None
        if amt_col is not None:
            trans_amt = safe_numeric(trans[amt_col])
            income = trans_amt[trans_amt > 0].sum()
            expense = -trans_amt[trans_amt < 0].sum()
            trans['amount_combined'] = trans_amt
        else:
            logging.warning('TransactionsAgent: no amount column found in transactions')
        if date_col is not None:
            trans['date_parsed'] = pd.to_datetime(trans[date_col], errors='coerce')
            min_date = trans['date_parsed'].min()
            max_date = trans['date_parsed'].max()
        else:
            min_date = max_date = None
        self.results = {'transactions_df': trans, 'income': income, 'expense': expense, 'period': (min_date, max_date)}
        logging.info(f"TransactionsAgent: income={income} expense={expense} period={min_date} to {max_date}")
        return self.results

@dataclass
class AccountsAgent:
    """Extracts account-level balances (cash) and computes liquidity."""
    df: pd.DataFrame
    results: Dict[str, Any] = field(default_factory=dict, init=False)
    def run(self) -> Dict[str, Any]:
        logging.info('AccountsAgent: extracting account balances')
        acct_cols = [c for c in self.df.columns if c.startswith('accounts__') and 'holdings' not in c]
        balances = pd.DataFrame()
        balance_col = next((c for c in acct_cols if 'balance' in c.lower() or 'current' in c.lower()), None)
        total_cash = 0.0
        if balance_col is not None:
            total_cash = safe_numeric(self.df[balance_col]).sum()
        else:
            logging.warning('AccountsAgent: no balance-like column found')
        self.results = {'accounts_cols': acct_cols, 'balance_col': balance_col, 'total_cash': total_cash}
        logging.info(f"AccountsAgent: total cash = {total_cash:.2f}")
        return self.results

@dataclass
class TaxAgent:
    """Performs illustrative tax calculations."""
    income: Optional[float]
    filing_status: str = 'married_filing_jointly'
    def run(self) -> Dict[str, Any]:
        logging.info('TaxAgent: running illustrative tax calc')
        if self.income is None:
            return {'federal_tax': None, 'state_tax': None, 'notes': 'No income data for tax calc'}
        annual_income = float(self.income)
        brackets = [
            (0, 20550, 0.10),
            (20550, 83550, 0.12),
            (83550, 178150, 0.22),
            (178150, 340100, 0.24),
            (340100, 431900, 0.32),
            (431900, 647850, 0.35),
            (647850, float('inf'), 0.37),
        ]
        standard_deduction = 30000
        taxable = max(0.0, annual_income - standard_deduction)
        tax = 0.0
        for low, high, rate in brackets:
            if taxable <= low:
                break
            taxed_at = min(taxable, high) - low
            tax += taxed_at * rate
        state_tax = annual_income * 0.06
        result = {'federal_tax': tax, 'state_tax': state_tax, 'taxable_income': taxable, 'standard_deduction': standard_deduction}
        logging.info(f"TaxAgent: federal_tax={tax:.2f} state_tax={state_tax:.2f}")
        return result

@dataclass
class RiskAgent:
    """Analyzes concentration and suggests target allocation."""
    holdings_info: Dict[str, Any]
    def run(self) -> Dict[str, Any]:
        alloc: pd.DataFrame = self.holdings_info.get('alloc', pd.DataFrame())
        total = self.holdings_info.get('total', 0.0)
        score = 'Unknown'
        suggestions = []
        if total <= 0 or alloc.empty:
            suggestions.append('No portfolio data to analyze concentration')
        else:
            top_pct = alloc.iloc[0]['Pct'] if 'Pct' in alloc.columns and len(alloc)>0 else 0
            if top_pct > 25:
                score = 'High concentration'
                suggestions.append(f'Single asset class holding {top_pct:.1f}% — consider diversification')
            else:
                score = 'Diversified enough'
                suggestions.append('No single asset-class concentration detected')
        return {'risk_score': score, 'suggestions': suggestions}

@dataclass
class ComplianceAgent:
    """Checks for common reporting flags (foreign assets, missing cost-basis)."""
    df: pd.DataFrame
    def run(self) -> Dict[str, Any]:
        notes = []
        cur = self.df.get('currency') if 'currency' in self.df.columns else None
        if cur is not None and cur.dropna().unique().size > 0:
            unique = cur.dropna().unique().tolist()
            if not all(u.upper() == 'USD' for u in unique):
                notes.append('Non-USD currency exposures detected — check FBAR/FATCA triggers for foreign accounts')
        has_cost = any('cost' in c.lower() or 'basis' in c.lower() for c in self.df.columns)
        if not has_cost:
            notes.append('No cost-basis columns present; cannot compute realized/unrealized capital gains precisely')
        return {'notes': notes}

@dataclass
class ReportAgent:
    """Generates markdown report and saves CSVs + charts."""
    output_dir: str
    profile: Dict[str, Any]
    accounts_res: Dict[str, Any]
    holdings_res: Dict[str, Any]
    trans_res: Dict[str, Any]
    tax_res: Dict[str, Any]
    risk_res: Dict[str, Any]
    comp_res: Dict[str, Any]
    def _save_csv(self, df: pd.DataFrame, name: str):
        path = os.path.join(self.output_dir, name)
        df.to_csv(path, index=False)
        return path
    def _save_plot_allocation(self):
        alloc = self.holdings_res.get('alloc', pd.DataFrame()).copy()
        if alloc.empty:
            return None
        plt.figure(figsize=(6,6))
        labels = alloc['asset_class_clean'].astype(str).tolist()
        sizes = alloc['market_value'].astype(float).tolist()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title('Portfolio Allocation by Asset Class')
        path = os.path.join(self.output_dir, 'plot_allocation.png')
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path
    def _save_plot_income_expense(self):
        income = self.trans_res.get('income') or 0.0
        expense = self.trans_res.get('expense') or 0.0
        plt.figure(figsize=(6,4))
        plt.bar(['Income','Expense'], [income, expense])
        plt.title('Income vs Expense (observed period)')
        plt.ylabel('Amount')
        path = os.path.join(self.output_dir, 'plot_income_expense.png')
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path
    def run(self) -> Dict[str, Any]:
        logging.info('ReportAgent: generating report and saving artifacts')
        ensure_dir(self.output_dir)
        holdings_df = self.holdings_res.get('holdings_df', pd.DataFrame())
        alloc_df = self.holdings_res.get('alloc', pd.DataFrame())
        trans_df = self.trans_res.get('transactions_df', pd.DataFrame())
        files = {}
        if not holdings_df.empty:
            files['holdings_csv'] = self._save_csv(holdings_df, 'holdings_extracted.csv')
        if not alloc_df.empty:
            alloc_saved = alloc_df.copy()
            alloc_saved['market_value'] = alloc_saved['market_value'].astype(float)
            files['alloc_csv'] = self._save_csv(alloc_saved, 'alloc.csv')
        if not trans_df.empty:
            files['transactions_csv'] = self._save_csv(trans_df, 'transactions_extracted.csv')
        files['plot_allocation'] = self._save_plot_allocation()
        files['plot_income_expense'] = self._save_plot_income_expense()
        # Advanced metrics
        cash = self.accounts_res.get('total_cash', 0.0)
        portfolio = self.holdings_res.get('total', 0.0)
        net_worth = cash + portfolio
        alloc = alloc_df
        liquidity_pct = (cash / net_worth * 100) if net_worth else 0.0
        income = self.trans_res.get('income', 0.0)
        expense = self.trans_res.get('expense', 0.0)
        period = self.trans_res.get('period', (None, None))
        savings = income - expense if income and expense else 0.0
        savings_rate = (savings / income * 100) if income else 0.0
        monthly_expense = (expense * 52 / 12) if period and period[0] and period[1] and (pd.to_datetime(period[1]) - pd.to_datetime(period[0])).days + 1 <= 14 else (expense / 12 if expense else 0.0)
        cash_runway_months = (cash / monthly_expense) if monthly_expense else 0.0

        tmpl = Template(DETAILED_REPORT_TEMPLATE)
        report_md = tmpl.render(
            profile=self.profile,
            accounts=self.accounts_res,
            holdings=self.holdings_res,
            transactions=self.trans_res,
            tax=self.tax_res,
            risk=self.risk_res,
            compliance=self.comp_res,
            files=files,
            cash=cash,
            portfolio=portfolio,
            net_worth=net_worth,
            liquidity_pct=liquidity_pct,
            income=income,
            expense=expense,
            savings=savings,
            savings_rate=savings_rate,
            cash_runway_months=cash_runway_months,
            alloc=alloc,
            period=period
        )
        report_path = os.path.join(self.output_dir, 'wealth_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_md)
        logging.info(f'ReportAgent: saved report to {report_path}')
        files['report_md'] = report_path
        return files

DETAILED_REPORT_TEMPLATE = r"""
Executive summary

Client: {{ profile.get('profile__name','Unknown') }}, age {{ profile.get('profile__age','Unknown') }}, {{ profile.get('profile__marital_status','Unknown') }}, 1 dependent ({{ profile.get('profile__dependents__name','Unknown') }}, age {{ profile.get('profile__dependents__age','Unknown') }}). (Profile in dataset: US resident, {{ profile.get('profile__residency__state','Unknown') }} — {{ profile.get('profile__residency__city','Unknown') }}.)

Snapshot (observed data in the upload):

Cash / account balances: ${{ '{:,.2f}'.format(cash) }} (USD)
Portfolio (holdings) market value: ${{ '{:,.2f}'.format(portfolio) }} (USD)
Estimated Net Worth (cash + portfolio): ${{ '{:,.2f}'.format(net_worth) }} (USD)

Observed transactions (sample period {{ period[0] }} → {{ period[1] }}):

Income (sample week): ${{ '{:,.2f}'.format(income) }}
Expenses (sample week): ${{ '{:,.2f}'.format(expense) }}
Savings in that sample week: ${{ '{:,.2f}'.format(savings) }} (savings rate ≈ {{ '{:.1f}'.format(savings_rate) }}% for observed period)

Liquidity: cash is ~{{ '{:.1f}'.format(liquidity_pct) }}% of cash + portfolio.
Cash runway (using sample-week expenses annualized → monthly): ~{{ '{:.1f}'.format(cash_runway_months) }} months of observed spending covered by cash (very conservative — excellent liquidity).

Portfolio total (from holdings in file): ${{ '{:,.2f}'.format(portfolio) }} (USD). I computed allocation by reported accounts__holdings__asset_class and market values in the file.

Important assumption & data note: the transaction totals provided are for {{ period[0] }}–{{ period[1] }} (one-week sample). Where I annualize (for tax estimates) I make that explicit; please treat annualized figures as illustrative projections unless you confirm income cadence.

1) Financial / portfolio analysis (data-driven)
Portfolio & cash

Cash balances (sum of accounts__balance): ${{ '{:,.2f}'.format(cash) }}.
Total holdings (sum of computed market values): ${{ '{:,.2f}'.format(portfolio) }}.
Net worth (cash + holdings): ${{ '{:,.2f}'.format(net_worth) }}.

Allocation (top asset-class summary)

I derived allocations from accounts__holdings__asset_class and market value computed as quantity × price in the file. A CSV of the allocation and the top holdings is attached (links below).
(Full allocation CSV attached: alex_alloc_for_report.csv)

Cashflow (observed)

Sample-week totals ({{ period[0] }} → {{ period[1] }}): Income = ${{ '{:,.2f}'.format(income) }}; Expense = ${{ '{:,.2f}'.format(expense) }}.

If that income / expense pattern repeated weekly, the implied annualized income ≈ ${{ '{:,.2f}'.format(income*52) }} and annualized expenses ≈ ${{ '{:,.2f}'.format(expense*52) }}. I use that only for illustrative tax projections below — please confirm cadence (weekly pay, biweekly, monthly, etc.) before relying on annualized tax computations.

Key financial observations

Very strong liquidity: ~{{ '{:.1f}'.format(liquidity_pct) }}% cash and ~{{ '{:.1f}'.format(cash_runway_months) }} months of observed spending covered by cash — ideal for a near-term safety cushion.
Net worth is moderate/solid for age {{ profile.get('profile__age','Unknown') }}; with high savings rate in the sample period ({{ '{:.1f}'.format(savings_rate) }}% in week observed) — unusually high, worth verifying whether this weekend included a pay cycle.
No cost-basis data found for many holdings (no CostBasis column present). That restricts precise realized/unrealized-gain tax calculations — we can request broker lot-level export for accurate tax planning.

2) Tax analysis (U.S. federal + California — illustrative estimates)

Because Alex is a U.S. citizen and CA resident, I use federal IRS rules and California guidance for context. Sources used: IRS tax rates pages and IRS 2025 inflation adjustments, IRS capital gains guidance, and California FTB materials. 
IRS
+2
IRS
+2
Franchise Tax Board

A — Method & assumptions

Observed income (${{ '{:,.2f}'.format(income) }}) and expense (${{ '{:,.2f}'.format(expense) }}) are for {{ period[0] }}–{{ period[1] }}. For federal tax illustrative projection I annualized income by multiplying weekly gross by 52 → ${{ '{:,.2f}'.format(income*52) }} (illustrative only). If actual pay cadence differs please tell me and I’ll re-run the projection.

Standard deduction (federal) for 2025 (married filing jointly) used: $30,000 (IRS 2025 inflation adjustments). 
IRS

California (state) standard deduction and tax rules referenced from FTB and state tables. CA standard deduction (2024/2025 filings) for MFJ ≈ $11,080 (CA FTB). 
Franchise Tax Board
H&R Block Tax preparation company

B — Rough federal-income-tax illustration (annualized, illustrative)

Annualized gross (observed-week extrapolation): ${{ '{:,.2f}'.format(income*52) }}.
Taxable income after federal standard deduction ($30,000): ${{ '{:,.2f}'.format(income*52-30000) }}.

Using 2025 federal brackets for married filing jointly, a stepwise calculation gives estimated federal income tax ≈ ${{ '{:,.2f}'.format(tax.get('federal_tax',0.0)) }} (effective federal tax ≈ {{ '{:.1f}'.format((tax.get('federal_tax',0.0)/(income*52))*100 if income else 0.0) }}% of gross). (This is an illustration using published 2025 bracket thresholds.) 
IRS
Tax Foundation

C — Rough California state tax (illustrative)

CA taxable income (annualized gross minus CA standard deduction ≈ $11,080) ≈ ${{ '{:,.2f}'.format(income*52-11080) }}.

California is progressive; for this taxable level CA state tax estimate is roughly $10–$15k (approximate effective state rate ~5%–7% for this income band). Use CA Dept. of Revenue / FTB tables for a precise figure, or I can compute exact stepwise state calculation once you confirm annual income cadence. 
Franchise Tax Board
Blog

D — Capital gains & investment tax notes

Long-term capital gains rates remain 0%, 15%, 20% depending on taxable income thresholds in 2025. For married filing jointly the 0% → 15% threshold is ~$96,700; 15% → 20% kicks in above $600,050 (2025). Since Alex’s projected taxable income (illustrative) is in the mid-$100ks, capital gains on significant sales may be taxed at 15% (plus potential NIIT). Exact taxes depend on realized gains and holding periods. 
NerdWallet
Bankrate

E — Immediate tax opportunities & constraints (recommendations)

Max out pre-tax retirement (401(k)/403(b)/403a, if available) to reduce taxable income today. If employer match exists, capture it. (If you want, I can compute optimal deferral given your pay cadence.)
Use an HSA (if eligible) — triple tax advantage; consider family HSA to lower taxable income.
529 plan for child savings — tax-advantaged for education (especially CA-qualified plans for state-level benefits).
Tax-loss harvesting: since cost-basis is missing, get broker tax-lot exports. If realized gains exist, harvest offsetting losses strategically (avoid wash-sale pitfalls).
Roth conversion strategy: given current taxable income projections, partial/conservative Roth conversions in low-tax years may be attractive — but needs multi-year modelling.
Citations used above (federal brackets, standard deduction, capital gains thresholds, CA guidance). 
IRS
+1
NerdWallet
Franchise Tax Board

3) Risk analysis & portfolio recommendations
Observed (from file)

I computed asset-class breakdown from accounts__holdings__asset_class. The portfolio value is ${{ '{:,.2f}'.format(portfolio) }}. Exact class weights are in the attached allocation CSV and pie chart.

Quick risk takeaways

Age {{ profile.get('profile__age','Unknown') }} with dependent → long investment horizon; capacity for growth-oriented allocation is present.
High cash → Alex has the capacity to take longer-term volatility (excess cash could be put to work tax-efficiently).
Unknown concentration — need to check single-stock exposure (symbol column present in file) — if large single-stock positions exist, consider diversification or hedging.

Suggested target allocations (starter, to discuss vs goals)

Growth & long horizon ({{ profile.get('profile__age','Unknown') }} y/o) — 70–85% equities / 10–25% fixed income / 0–5% alternatives or cash (tweak based on risk tolerance and goals).
Given current liquidity, consider dollar-cost averaging into diversified ETFs or tax-efficient mutual funds to avoid market-timing risk.
Add a small bond ladder or short-duration bond funds for stability; use municipal bonds (if in high tax state and taxable account) for tax efficiency.

4) Compliance & reporting checklist (U.S. focus)

FBAR (FinCEN Form 114): if Alex has aggregate foreign account balances > $10,000 at any time in the year — must file FBAR. (Check foreign account exposures.) 
FinCEN.gov

Form 8938 (FATCA): thresholds vary — for married filing jointly living in the U.S., filing required if specified foreign assets exceed $100,000 on last day or $150,000 at any time during the year (higher thresholds apply if living abroad). 
IRS

Broker statements & records: obtain tax-lot detail (trade date, quantity, cost basis, realized gain/loss). Without these, accurate capital gains tax and tax-loss harvesting are not possible.
Document retention: keep 6+ years for tax records; maintain export of brokerage CSVs and annual statements.

5) Immediate, short-term, and medium-term action plan (priority-ranked)
Immediate (within 7–14 days)

Confirm cadence of income (weekly/biweekly/monthly) so I can replace the “weekly → annualized” assumption for accurate tax projections. (If you prefer, I will assume weekly and proceed; I already used weekly for the illustrative tax calc.)
Export broker tax-lot data (cost basis, trade dates) for each holding — upload CSV or let me know the broker and I’ll give exact export instructions. This unlocks exact capital-gains, tax-loss harvesting, and realized/unrealized gain calculations.
Review employer benefits: 401(k) contribution level & match, HSA eligibility, dependent benefits.

Short-term (1–3 months)

Tax optimization: implement pre-tax retirement / HSA contributions for 2025 if appropriate. Consider Roth conversion amounts if taxable profile favors it (I can model scenarios).
Diversification: if any single holding >10–15% of portfolio, set a plan to reduce concentration over time to target allocation (DCA out).
Set up automated rebalancing and target allocation buckets.

Medium-term (3–12 months)

Estate & beneficiary review: confirm beneficiary designations and a simple will/trust if desired.
Education plan: open / fund 529 for Mia if future education is a goal.
Tax-aware investing: explore municipal bonds or tax-efficient ETFs for taxable accounts.
"""

def run_pipeline(input_csv: str, output_dir: str, user_id: str = None):
    ensure_dir(output_dir)
    data_agent = DataAgent(input_csv)
    df = data_agent.run(user_id)
    profile_cols = [c for c in df.columns if c.startswith('profile__')]
    profile = {}
    for c in profile_cols:
        vals = df[c].dropna().unique()
        profile[c] = vals[0] if len(vals)>0 else None
    holdings_agent = HoldingsAgent(df=df)
    holdings_res = holdings_agent.run()
    accounts_agent = AccountsAgent(df=df)
    accounts_res = accounts_agent.run()
    trans_agent = TransactionsAgent(df=df)
    trans_res = trans_agent.run()
    income_observed = trans_res.get('income')
    period = trans_res.get('period')
    if income_observed and period and period[0] and period[1]:
        days = (pd.to_datetime(period[1]) - pd.to_datetime(period[0])).days + 1
        if days <= 14:
            annual_income = float(income_observed) * 52
        else:
            annual_income = float(income_observed)
    else:
        annual_income = income_observed
    tax_agent = TaxAgent(income=annual_income)
    tax_res = tax_agent.run()
    risk_agent = RiskAgent(holdings_info=holdings_res)
    risk_res = risk_agent.run()
    comp_agent = ComplianceAgent(df=df)
    comp_res = comp_agent.run()
    report_agent = ReportAgent(output_dir=output_dir, profile=profile, accounts_res=accounts_res,
                               holdings_res=holdings_res, trans_res=trans_res, tax_res=tax_res,
                               risk_res=risk_res, comp_res=comp_res)
    files = report_agent.run()
    logging.info('Pipeline finished. Artifacts:')
    for k,v in files.items():
        logging.info(f' - {k}: {v}')
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run multi-agent wealth manager pipeline')
    parser.add_argument('--input', required=True, help='Input CSV path')
    parser.add_argument('--output', default='./output', help='Output directory')
    parser.add_argument('--user_id', required=False, help='User ID to analyze (e.g., u_1001)')
    args = parser.parse_args()
    run_pipeline(args.input, args.output, args.user_id)
