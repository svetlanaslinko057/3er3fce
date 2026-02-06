/**
 * Graph State Service
 * P2.2: Share / Persist Graph State
 * 
 * Handles:
 * - Encode state → base64 URL-safe string
 * - Decode state → validate & return
 * - Version control for backward compatibility
 */

export interface GraphStateV1 {
  version: '1.0';
  
  // UI Filters
  filters?: {
    profiles?: string[];
    early_signal?: string[];
    risk_level?: string[];
    edge_strength?: string[];
    hide_isolated?: boolean;
    limit_nodes?: number;
  };
  
  // Selection
  selected_nodes?: string[];  // account_id[]
  selectedNodes?: string[];   // alias for backward compat
  
  // Compare mode
  compare?: {
    left?: string;
    right?: string;
    nodeA?: string;  // alias
    nodeB?: string;  // alias
    active?: boolean;
  } | null;
  
  // View state
  view?: 'graph' | 'table' | 'compare';
  
  // Table sorting
  sort?: {
    field?: string;
    order?: 'asc' | 'desc';
  };
  table?: {
    sortBy?: string;
    order?: 'asc' | 'desc';
  };
  
  // Focus/Highlight
  focus?: string;       // account_id to focus on load
  highlight?: string;   // alias for focus
}

const CURRENT_VERSION = '1.0';

/**
 * Encode graph state to URL-safe base64
 */
export function encodeGraphState(state: Partial<GraphStateV1>): string {
  const fullState: GraphStateV1 = {
    version: CURRENT_VERSION,
    ...state,
  };
  
  // Remove undefined/null values
  const cleaned = JSON.parse(JSON.stringify(fullState));
  
  // Convert to JSON, then base64
  const json = JSON.stringify(cleaned);
  const base64 = Buffer.from(json, 'utf-8').toString('base64');
  
  // Make URL-safe (replace + with -, / with _, remove =)
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Decode URL-safe base64 to graph state
 */
export function decodeGraphState(encoded: string): GraphStateV1 | null {
  try {
    // Restore base64 padding and chars
    let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) {
      base64 += '=';
    }
    
    const json = Buffer.from(base64, 'base64').toString('utf-8');
    const state = JSON.parse(json) as GraphStateV1;
    
    // Validate version
    if (!state.version) {
      console.warn('[GraphState] Missing version, assuming v1.0');
      state.version = '1.0';
    }
    
    // Version check
    if (state.version !== CURRENT_VERSION) {
      console.warn(`[GraphState] Version mismatch: ${state.version} vs ${CURRENT_VERSION}`);
      // Could add migration logic here for future versions
    }
    
    return state;
  } catch (err) {
    console.error('[GraphState] Decode error:', err);
    return null;
  }
}

/**
 * Validate graph state structure
 */
export function validateGraphState(state: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (!state || typeof state !== 'object') {
    return { valid: false, errors: ['State must be an object'] };
  }
  
  // Version check
  if (state.version && state.version !== CURRENT_VERSION) {
    errors.push(`Unknown version: ${state.version}`);
  }
  
  // Filters validation
  if (state.filters) {
    if (state.filters.profiles && !Array.isArray(state.filters.profiles)) {
      errors.push('filters.profiles must be an array');
    }
    if (state.filters.limit_nodes && (typeof state.filters.limit_nodes !== 'number' || state.filters.limit_nodes < 1)) {
      errors.push('filters.limit_nodes must be a positive number');
    }
  }
  
  // Selected nodes validation
  if (state.selectedNodes && !Array.isArray(state.selectedNodes)) {
    errors.push('selectedNodes must be an array');
  }
  
  // View validation
  if (state.view && !['graph', 'table'].includes(state.view)) {
    errors.push('view must be "graph" or "table"');
  }
  
  return { valid: errors.length === 0, errors };
}

/**
 * Create shareable URL for graph state
 */
export function createShareUrl(baseUrl: string, state: Partial<GraphStateV1>): string {
  const encoded = encodeGraphState(state);
  return `${baseUrl}?state=${encoded}`;
}
