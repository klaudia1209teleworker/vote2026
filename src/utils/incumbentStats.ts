export type IncumbentInterpellationItem = {
  date?: string;
  dateAsRecorded?: string;
  time?: string;
  session?: string;
  department?: string;
  title?: string;
  councillorsAsRecorded?: string;
  listedAs?: string;
  sourceUrl?: string;
  videoUrl?: string;
  transcriptUrl?: string;
  documentUrl?: string;
};

export type ProposalItem = {
  session?: string;
  title?: string;
  outcome?: Record<string, string | null>;
  sourceUrl?: string;
};

export type PlenaryCounts = {
  attended: number;
  denominator: number;
  excludedBothLists: number;
};

export type AttendanceInfo = {
  status?: 'available' | 'missing' | string;
  /** 大會出席率，0–100。 */
  plenary?: number | null;
  committee?: number | null;
  plenaryCounts?: PlenaryCounts;
  reason?: string;
  checkedOn?: string;
  sourceUrl?: string;
};

export type IncumbentEntry = {
  incumbency: {
    publish: boolean;
    matchMethod?: string;
    rosterName?: string;
    rosterDistrict?: string;
    rosterNote?: string;
    rosterSourceUrl?: string;
    profileUrl?: string;
  };
  attendance?: AttendanceInfo;
  interpellation?: {
    kind?: string;
    count?: number;
    sourceUrl?: string;
    note?: string;
    status?: string;
    reason?: string;
    term?: string;
    totalCount?: number;
    totalCountNote?: string;
    items?: IncumbentInterpellationItem[];
  };
  proposals?: {
    kind?: string;
    note?: string;
    count?: number;
    sourceUrl?: string;
    reason?: string;
    status?: string;
    asProposer?: {
      count?: number;
      sourceUrl?: string;
      items?: ProposalItem[];
    };
    asCoSigner?: {
      count?: number;
      sourceUrl?: string;
    };
  };
};

export type DistrictAverages = {
  attendancePlenary: number | null;
  attendanceCommittee: number | null;
  interpellation: number | null;
  proposals: number | null;
  sampleSize: {
    attendancePlenary: number;
    attendanceCommittee: number;
    interpellation: number;
    proposals: number;
  };
};

function districtKeyFromIncumbentKey(key: string): string {
  const parts = key.split('|');
  return parts.slice(0, 3).join('|');
}

export function getInterpellationCount(entry: IncumbentEntry): number | null {
  const inter = entry.interpellation;
  if (!inter) return null;
  if (typeof inter.count === 'number') return inter.count;
  if (typeof inter.totalCount === 'number') return inter.totalCount;
  if (inter.items && inter.items.length > 0) return inter.items.length;
  return null;
}

/** 提案數量：優先提案人筆數；臺北等未區分角色則用 proposals.count */
export function getProposalCount(entry: IncumbentEntry): number | null {
  const props = entry.proposals;
  if (!props) return null;
  if (props.asProposer) {
    if (typeof props.asProposer.count === 'number') return props.asProposer.count;
    if (props.asProposer.items && props.asProposer.items.length > 0) {
      return props.asProposer.items.length;
    }
  }
  if (typeof props.count === 'number') return props.count;
  return null;
}

export function getProposalItems(entry: IncumbentEntry): ProposalItem[] {
  return entry.proposals?.asProposer?.items ?? [];
}

function mean(values: number[]): number | null {
  if (values.length === 0) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * 依選區（縣市|職位|選區）計算 publish:true 現任者的均值。
 * 僅納入該指標有數值的人；不把缺失當成 0。
 */
export function buildDistrictAverages(
  incumbents: Record<string, IncumbentEntry | { version?: string }>
): Record<string, DistrictAverages> {
  const buckets = new Map<
    string,
    {
      attendancePlenary: number[];
      attendanceCommittee: number[];
      interpellation: number[];
      proposals: number[];
    }
  >();

  for (const [key, raw] of Object.entries(incumbents)) {
    if (key === 'metadata') continue;
    const entry = raw as IncumbentEntry;
    if (!entry?.incumbency?.publish) continue;

    const dKey = districtKeyFromIncumbentKey(key);
    let bucket = buckets.get(dKey);
    if (!bucket) {
      bucket = {
        attendancePlenary: [],
        attendanceCommittee: [],
        interpellation: [],
        proposals: [],
      };
      buckets.set(dKey, bucket);
    }

    const att = entry.attendance;
    if (att?.status === 'available') {
      if (typeof att.plenary === 'number') bucket.attendancePlenary.push(att.plenary);
      if (typeof att.committee === 'number') bucket.attendanceCommittee.push(att.committee);
    }

    const interCount = getInterpellationCount(entry);
    if (interCount != null) bucket.interpellation.push(interCount);

    const propCount = getProposalCount(entry);
    if (propCount != null) bucket.proposals.push(propCount);
  }

  const result: Record<string, DistrictAverages> = {};
  for (const [dKey, bucket] of buckets) {
    result[dKey] = {
      attendancePlenary: mean(bucket.attendancePlenary),
      attendanceCommittee: mean(bucket.attendanceCommittee),
      interpellation: mean(bucket.interpellation),
      proposals: mean(bucket.proposals),
      sampleSize: {
        attendancePlenary: bucket.attendancePlenary.length,
        attendanceCommittee: bucket.attendanceCommittee.length,
        interpellation: bucket.interpellation.length,
        proposals: bucket.proposals.length,
      },
    };
  }
  return result;
}

export function formatMetricRatio(
  value: number | null,
  average: number | null,
  opts?: { asPercent?: boolean; digits?: number }
): string {
  const digits = opts?.digits ?? (opts?.asPercent ? 1 : 1);
  const fmt = (n: number) => {
    const rounded = Number(n.toFixed(digits));
    if (opts?.asPercent) return `${rounded}%`;
    return Number.isInteger(rounded) ? String(rounded) : String(rounded);
  };
  const left = value == null ? '—' : fmt(value);
  const right = average == null ? '—' : fmt(average);
  return `${left}/${right}`;
}

export function attendanceUnavailableLabel(attendance?: AttendanceInfo): string {
  if (!attendance) return '尚未整理';
  if (attendance.status === 'available') return '';
  if (attendance.reason?.includes('未找到')) return '議會未公開可統計資料';
  if (attendance.reason === '尚未整理' || attendance.reason?.includes('未擷取')) {
    return '尚未整理';
  }
  return attendance.reason?.includes('未公開')
    ? '議會未公開可統計資料'
    : '尚未整理';
}
