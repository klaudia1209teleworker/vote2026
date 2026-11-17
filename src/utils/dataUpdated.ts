// 建置時計算全站資料最近更新日期：取各資料檔中 lastVerified / asOf / lastUpdated 欄位的最大值。
import candidates from '../data/candidates.json';
import bulletin from '../data/bulletin.json';
import incumbents from '../data/incumbents.json';

const DATE_FIELDS = ['lastVerified', 'asOf', 'lastUpdated'];
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function maxDate(records: unknown[]): string {
  let max = '';
  for (const r of records) {
    if (!r || typeof r !== 'object') continue;
    for (const f of DATE_FIELDS) {
      const v = (r as Record<string, unknown>)[f];
      if (typeof v === 'string' && DATE_RE.test(v) && v > max) max = v;
    }
  }
  return max;
}

export const dataUpdatedAt: string = [
  maxDate(candidates as unknown[]),
  maxDate(Object.values(bulletin as Record<string, unknown>)),
  maxDate(Object.values(incumbents as Record<string, unknown>)),
].reduce((a, b) => (b > a ? b : a), '');
