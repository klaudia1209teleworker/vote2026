import candidatesData from '../data/candidates.json';
import districtsData from '../data/districts.json';
import positionsData from '../data/positions.json';
import electoralData from '../data/electoralDistricts.json';

type CandidateRow = {
  county: string;
  position: string;
  district?: string | null;
};

type CouncilDistrict = {
  name: string;
  seats?: number;
  isIndigenous?: boolean;
  indigenousType?: string;
};

type CityRecord = {
  type: string;
  districts?: string[];
  mountainIndigenousDistricts?: string[];
};

const candidates = candidatesData as CandidateRow[];
const cities = districtsData.cities as Record<string, CityRecord>;
const positionMeta = new Map(
  positionsData.positions.map((position) => [
    position.id,
    { name: position.name, shortName: position.shortName || position.name },
  ]),
);
const councilDistricts = electoralData.councilDistricts as Record<
  string,
  { districts?: CouncilDistrict[] }
>;

const POSITION_ORDER = [
  'mayor-municipal',
  'mayor-county',
  'councilor-municipal',
  'councilor-county',
  'district-mayor',
  'district-representative',
  'township-mayor',
  'township-representative',
  'village-chief',
] as const;

export type AreaLink = {
  name: string;
  count: number;
  href: string;
  note?: string;
};

export type PositionGroup = {
  id: string;
  name: string;
  shortName: string;
  count: number;
  listHref: string | null;
  areas: AreaLink[];
};

export type CityNav = {
  city: string;
  type: string;
  total: number;
  positions: PositionGroup[];
};

function districtPath(positionId: string, city: string, area?: string): string {
  const encodedCity = encodeURIComponent(city);
  if (!area) return `candidates/district/${positionId}/${encodedCity}/`;
  return `candidates/district/${positionId}/${encodedCity}/${encodeURIComponent(area)}/`;
}

export function cityHubPath(city: string, hash?: string): string {
  const path = `candidates/city/${encodeURIComponent(city)}/`;
  return hash ? `${path}#${hash}` : path;
}

export function positionEntryPath(city: string, position: PositionGroup): string {
  if (position.areas.length === 0 && position.listHref) return position.listHref;
  return cityHubPath(city, position.id);
}

function applies(positionId: string, cityType: string, hasMountain: boolean): boolean {
  switch (positionId) {
    case 'mayor-municipal':
    case 'councilor-municipal':
      return cityType === '直轄市';
    case 'mayor-county':
    case 'councilor-county':
      return cityType === '縣' || cityType === '省轄市';
    case 'township-mayor':
    case 'township-representative':
      return cityType === '縣';
    case 'district-mayor':
    case 'district-representative':
      return cityType === '直轄市' && hasMountain;
    case 'village-chief':
      return true;
    default:
      return false;
  }
}

function indigenousNote(district: CouncilDistrict): string | undefined {
  if (!district.isIndigenous) return undefined;
  return district.indigenousType === 'plains' ? '平地原住民' : '山地原住民';
}

function buildCity(city: string): CityNav | null {
  const cityData = cities[city];
  if (!cityData) return null;

  const cityCandidates = candidates.filter((candidate) => candidate.county === city);
  const hasMountain = (cityData.mountainIndigenousDistricts?.length ?? 0) > 0;
  const positions: PositionGroup[] = [];

  for (const positionId of POSITION_ORDER) {
    if (!applies(positionId, cityData.type, hasMountain)) continue;

    const meta = positionMeta.get(positionId);
    const rows = cityCandidates.filter((candidate) => candidate.position === positionId);
    const isCouncilor = positionId.startsWith('councilor');
    const isMountain = positionId === 'district-mayor' || positionId === 'district-representative';
    const isMayor = positionId === 'mayor-municipal' || positionId === 'mayor-county';

    let areas: AreaLink[] = [];
    if (isCouncilor) {
      areas = (councilDistricts[city]?.districts ?? []).map((district) => ({
        name: district.name,
        count: rows.filter((candidate) => candidate.district === district.name).length,
        href: districtPath(positionId, city, district.name),
        note: indigenousNote(district),
      }));
    } else if (isMountain) {
      areas = (cityData.mountainIndigenousDistricts ?? []).map((name) => ({
        name,
        count: rows.filter((candidate) => candidate.district === name).length,
        href: districtPath(positionId, city, name),
      }));
    } else if (!isMayor) {
      areas = (cityData.districts ?? []).map((name) => ({
        name,
        count: rows.filter((candidate) => candidate.district === name).length,
        href: districtPath(positionId, city, name),
      }));
    }

    positions.push({
      id: positionId,
      name: meta?.name || positionId,
      shortName: meta?.shortName || positionId,
      count: rows.length,
      listHref: isMayor || isCouncilor ? districtPath(positionId, city) : null,
      areas,
    });
  }

  return {
    city,
    type: cityData.type,
    total: cityCandidates.length,
    positions,
  };
}

const navByCity = new Map<string, CityNav>();
for (const city of Object.keys(cities)) {
  const nav = buildCity(city);
  if (nav) navByCity.set(city, nav);
}

export function getCityCandidateNav(city: string): CityNav | null {
  return navByCity.get(city) ?? null;
}
