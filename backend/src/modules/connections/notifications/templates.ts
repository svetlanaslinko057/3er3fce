/**
 * Connections Telegram Notifications - Message Templates
 * Phase 2.3: Telegram Alerts Delivery
 * 
 * Messaging Specification v1.0
 */

import type { ConnectionsAlertEvent, ConnectionsAlertType } from './types.js';

// ============================================================
// FORMATTERS
// ============================================================

function fmtInt(n?: number): string {
  if (n === undefined || n === null) return '—';
  return Math.round(n).toString();
}

function fmtPct(n?: number): string {
  if (n === undefined || n === null) return '—';
  const v = Math.round(n);
  return `${v > 0 ? '+' : ''}${v}%`;
}

function fmtProfile(p?: string): string {
  if (!p) return '—';
  if (p === 'retail') return 'Retail';
  if (p === 'influencer') return 'Influencer';
  if (p === 'whale') return 'Whale';
  return p;
}

function fmtRisk(r?: string): string {
  if (!r) return '—';
  return r.charAt(0).toUpperCase() + r.slice(1);
}

function fmtTrend(t?: string): string {
  if (!t) return '—';
  return t.toUpperCase();
}

// ============================================================
// LINK BUILDERS
// ============================================================

export function buildConnectionsLink(baseUrl: string, accountId: string): string {
  const clean = baseUrl?.replace(/\/+$/, '') || '';
  return `${clean}/connections/${encodeURIComponent(accountId)}`;
}

export function buildRadarLink(baseUrl: string): string {
  const clean = baseUrl?.replace(/\/+$/, '') || '';
  return `${clean}/connections/radar`;
}

/**
 * P2.2.4: Build Graph link with state (highlight specific node)
 */
export function buildGraphLinkWithState(baseUrl: string, accountId: string): string {
  const clean = baseUrl?.replace(/\/+$/, '') || '';
  // Simple state: just highlight the account
  const state = {
    version: '1.0',
    highlight: accountId,
    view: 'graph',
  };
  const encoded = Buffer.from(JSON.stringify(state), 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  return `${clean}/connections/graph?state=${encoded}`;
}

// ============================================================
// MESSAGE TEMPLATES
// ============================================================

/**
 * Format Telegram message based on alert type
 * Following Messaging Specification v1.0
 */
export function formatTelegramMessage(baseUrl: string, e: ConnectionsAlertEvent): string {
  const username = e.username ? `@${e.username}` : e.account_id;
  const link = buildConnectionsLink(baseUrl, e.account_id);

  // TEST message
  if (e.type === 'TEST') {
    return [
      '🧪 TEST ALERT',
      '',
      'This is a test notification from Connections module.',
      '',
      'If you see this message — Telegram delivery is configured correctly.',
      'No real signals were used.',
    ].join('\n');
  }

  // 🚀 EARLY BREAKOUT
  if (e.type === 'EARLY_BREAKOUT') {
    const graphLink = buildGraphLinkWithState(baseUrl, e.account_id);
    return [
      '🚀 EARLY BREAKOUT',
      '',
      username,
      '',
      'Account shows early influence growth that the market hasn\'t noticed yet.',
      '',
      `• Influence: ${fmtInt(e.influence_score)}`,
      `• Acceleration: ${fmtPct(e.acceleration_pct)}`,
      `• Profile: ${fmtProfile(e.profile)}`,
      `• Risk: ${fmtRisk(e.risk)}`,
      '',
      e.explain_summary || 'Signal based on sustained growth and positive dynamics.',
      '',
      '🔗 View details:',
      link,
      '',
      '📊 Open in Graph:',
      graphLink,
    ].join('\n');
  }

  // 📈 STRONG ACCELERATION
  if (e.type === 'STRONG_ACCELERATION') {
    const graphLink = buildGraphLinkWithState(baseUrl, e.account_id);
    return [
      '📈 STRONG ACCELERATION',
      '',
      username,
      '',
      'Sharp acceleration of influence growth over a short period.',
      '',
      `• Influence: ${fmtInt(e.influence_score)}`,
      `• Velocity: +${fmtInt(e.velocity_per_day)}/day`,
      `• Acceleration: ${fmtPct(e.acceleration_pct)}`,
      `• Trend: ${fmtTrend(e.trend_state)}`,
      '',
      e.explain_summary || 'Dynamics intensifying, possible transition to breakout.',
      '',
      '🔗 View trend:',
      link,
      '',
      '📊 Open in Graph:',
      graphLink,
    ].join('\n');
  }

  // 🔄 TREND REVERSAL
  if (e.type === 'TREND_REVERSAL') {
    const graphLink = buildGraphLinkWithState(baseUrl, e.account_id);
    return [
      '🔄 TREND CHANGE',
      '',
      username,
      '',
      'Influence trend has changed.',
      '',
      `• Previous: ${fmtTrend(e.prev_trend_state)}`,
      `• Current: ${fmtTrend(e.trend_state)}`,
      `• Influence: ${fmtInt(e.influence_score)}`,
      '',
      e.explain_summary || 'Account dynamics changed — reassessment recommended.',
      '',
      '🔗 View analysis:',
      link,
      '',
      '📊 Open in Graph:',
      graphLink,
    ].join('\n');
  }

  // Fallback
  return [
    '🔔 CONNECTIONS ALERT',
    '',
    username,
    '',
    e.explain_summary || 'Alert triggered.',
    '',
    link,
  ].join('\n');
}
