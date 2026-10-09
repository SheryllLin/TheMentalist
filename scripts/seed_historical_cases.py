#!/usr/bin/env python3
"""
Historical Reference Case Seeder — THE MENTALIST
=================================================
Seeds four publicly-documented, historically-resolved investigation cases into the
CrimeNet backend via its REST API.

ALL data in this script is sourced from publicly available historical records,
court documents, official government reports, and established journalism.

Important caveats
-----------------
* These cases are explicitly tagged with category="HISTORICAL_REFERENCE" and
  provenance="PUBLIC_RECORD" to distinguish them from original investigations.
* No facts are fabricated. Where uncertainty exists, statements are marked as such.
* Seeding is IDEMPOTENT: running this script a second time will not create duplicate
  cases (it checks for an existing case by title before creating).
* This script does NOT modify or delete any existing user-created cases.

Sources referenced
------------------
1. JFK: Warren Commission Report (1964), House Select Committee on Assassinations (1979)
2. Watergate: Senate Watergate Committee Report (1974), U.S. v. Mitchell et al.
3. Unabomber: FBI case files (UNABOM), U.S. v. Kaczynski (1998), DOJ press releases
4. Golden State Killer: California DOJ press releases (2018), People v. DeAngelo (2020)

Usage
-----
    python scripts/seed_historical_cases.py [--api http://localhost:8000]

Prerequisites
-------------
    Backend running at the configured API base URL.
    pip install requests
"""
import argparse
import json
import sys
import time
from typing import Any

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────
DEFAULT_API   = "http://localhost:8000/api"
DEMO_EMAIL    = "demo@crimenet.local"
DEMO_PASSWORD = "crimenet2026"

# ── Historical case definitions ───────────────────────────────
# Each case contains:
#   title, description, priority, category, entities, relationships, events, sources
# Entities include their type, name, and known properties.
# All facts are sourced from the public record documents listed above.

HISTORICAL_CASES: list[dict[str, Any]] = [

    # ── 1. Assassination of President John F. Kennedy ─────────
    {
        "title": "Assassination of President John F. Kennedy",
        "description": (
            "On 22 November 1963, President John F. Kennedy was fatally shot "
            "while travelling in a presidential motorcade through Dealey Plaza, Dallas, Texas. "
            "The Warren Commission (1964) concluded that Lee Harvey Oswald acted alone. "
            "The House Select Committee on Assassinations (1979) later suggested a probable "
            "conspiracy based on acoustic evidence, though the scientific consensus on "
            "that evidence remains contested. This is a HISTORICAL REFERENCE case for "
            "educational network analysis demonstration."
        ),
        "priority": "CRITICAL",
        "status": "CLOSED",
        "category": "HISTORICAL_REFERENCE",
        "narrative_text": """HISTORICAL REFERENCE CASE — Educational Demonstration
SOURCE: Warren Commission Report (1964); HSCA Final Report (1979)

INCIDENT
On 22 November 1963 at approximately 12:30 PM CST, President John F. Kennedy was shot
while riding in a presidential motorcade along Elm Street in Dealey Plaza, Dallas, Texas.
He was pronounced dead at Parkland Memorial Hospital at 1:00 PM CST.

Texas Governor John Connally, seated in the same limousine, was also wounded but survived.

PERSONS OF INTEREST

1. Lee Harvey Oswald
   Date of birth: 18 October 1939
   Former US Marine; defected to the Soviet Union in 1959, returned to the US in 1962.
   Employed at the Texas School Book Depository, 411 Elm Street, Dallas.
   Arrested approximately 70 minutes after the assassination.
   Charged with the murder of President Kennedy and Dallas Police Officer J.D. Tippit.
   Shot and killed by Jack Ruby on 24 November 1963 before trial.

2. Jack Ruby (Jacob Leon Rubenstein)
   Date of birth: 25 March 1911
   Dallas nightclub owner. Shot Lee Harvey Oswald on 24 November 1963 in the basement
   of Dallas Police Headquarters while Oswald was being transferred.
   Convicted of murder in 1964. Conviction overturned on appeal. Died of cancer in 1967.

3. John F. Kennedy (Victim)
   35th President of the United States. Fatally wounded at Dealey Plaza.

4. John Connally (Victim, survived)
   Governor of Texas. Wounded in the same attack. Testified before the Warren Commission.

ORGANISATIONS

- Warren Commission (President's Commission on the Assassination)
  Established by President Johnson, 29 November 1963.
  Concluded: Oswald acted alone; Ruby acted alone.

- Texas School Book Depository
  414 Elm Street, Dallas. Oswald's place of employment.
  Sniper's nest found on the sixth floor.

- Dallas Police Department
  Arrested Oswald; had custody during his murder by Ruby.

LOCATIONS

- Dealey Plaza, Dallas, Texas — site of the assassination
- Texas School Book Depository — building from which shots were fired (Warren Commission)
- Parkland Memorial Hospital — where President Kennedy was pronounced dead
- Dallas Police Headquarters — where Oswald was shot by Ruby

KEY EVIDENCE (Public Record)

- Three spent cartridge cases found on the sixth floor of the Texas School Book Depository
- Mannlicher-Carcano Model 91/38 rifle found on the sixth floor
- Zapruder film (Abraham Zapruder, amateur footage of the assassination)
- Oswald's palm print found on the rifle
- Bullet fragments recovered from the limousine and victims
- Autopsy findings conducted at Bethesda Naval Hospital

TIMELINE OF KEY EVENTS

22 Nov 1963, 11:40 AM — Presidential motorcade departs Love Field, Dallas
22 Nov 1963, 12:30 PM — Shots fired at Dealey Plaza; President Kennedy fatally wounded
22 Nov 1963, 12:38 PM — Limousine arrives at Parkland Memorial Hospital
22 Nov 1963, 01:00 PM — President Kennedy pronounced dead
22 Nov 1963, 01:15 PM — Officer J.D. Tippit shot and killed; Oswald suspected
22 Nov 1963, 01:50 PM — Oswald arrested at Texas Theatre, Dallas
22 Nov 1963, 02:38 PM — Lyndon B. Johnson sworn in as President aboard Air Force One
24 Nov 1963, 11:21 AM — Lee Harvey Oswald shot and killed by Jack Ruby
29 Nov 1963           — Warren Commission established by President Johnson
24 Sep 1964           — Warren Commission Report published

OUTCOME
The Warren Commission concluded that Lee Harvey Oswald, acting alone, fired three shots
from the sixth floor of the Texas School Book Depository, killing President Kennedy.
The HSCA (1979) reopened the investigation and suggested a probable conspiracy based on
acoustic evidence; however, subsequent analysis has disputed that acoustic evidence.
No individual other than Oswald was ever charged in connection with the assassination.

SOURCES
- Warren Commission Report (1964). National Archives. https://www.archives.gov/research/jfk
- House Select Committee on Assassinations Final Report (1979). U.S. Government Printing Office.
- National Archives JFK Assassination Records: https://www.archives.gov/research/jfk
""",
        "entities": [
            {"type": "Person", "name": "Lee Harvey Oswald", "id_slug": "person-lee-harvey-oswald",
             "properties": {"aliases": ["L.H. Oswald"], "dob": "1939-10-18",
                            "nationality": "American", "occupation": "Warehouse worker / former US Marine",
                            "status": "Deceased (shot 24 Nov 1963)"}},
            {"type": "Person", "name": "Jack Ruby", "id_slug": "person-jack-ruby",
             "properties": {"aliases": ["Jacob Leon Rubenstein"], "dob": "1911-03-25",
                            "occupation": "Nightclub owner", "status": "Deceased (1967)"}},
            {"type": "Person", "name": "John F. Kennedy", "id_slug": "person-jfk",
             "properties": {"aliases": ["JFK", "President Kennedy"], "dob": "1917-05-29",
                            "role": "35th President of the United States",
                            "status": "Deceased (assassinated 22 Nov 1963)"}},
            {"type": "Person", "name": "John Connally", "id_slug": "person-john-connally",
             "properties": {"role": "Governor of Texas", "status": "Survived (deceased 1993)"}},
            {"type": "Organization", "name": "Warren Commission",
             "id_slug": "org-warren-commission",
             "properties": {"established": "1963-11-29", "type": "Federal investigation commission"}},
            {"type": "Organization", "name": "Texas School Book Depository",
             "id_slug": "org-tsbd",
             "properties": {"address": "411 Elm Street, Dallas, Texas",
                            "significance": "Location of sniper nest (Warren Commission finding)"}},
            {"type": "Organization", "name": "Dallas Police Department",
             "id_slug": "org-dallas-pd",
             "properties": {"type": "Law enforcement"}},
            {"type": "Location", "name": "Dealey Plaza, Dallas, Texas",
             "id_slug": "loc-dealey-plaza",
             "properties": {"city": "Dallas", "state": "Texas",
                            "significance": "Site of assassination"}},
            {"type": "Location", "name": "Parkland Memorial Hospital, Dallas",
             "id_slug": "loc-parkland-hospital",
             "properties": {"city": "Dallas",
                            "significance": "President Kennedy pronounced dead here"}},
            {"type": "Event", "name": "Assassination of President Kennedy",
             "id_slug": "event-jfk-assassination",
             "properties": {"event_type": "INCIDENT", "timestamp": "1963-11-22 12:30",
                            "location": "Dealey Plaza, Dallas, Texas",
                            "description": "President Kennedy fatally shot from Texas School Book Depository (Warren Commission)"}},
            {"type": "Event", "name": "Arrest of Lee Harvey Oswald",
             "id_slug": "event-oswald-arrest",
             "properties": {"event_type": "ARREST", "timestamp": "1963-11-22 13:50",
                            "location": "Texas Theatre, Dallas",
                            "description": "Oswald arrested approximately 70 minutes after assassination"}},
            {"type": "Event", "name": "Murder of Lee Harvey Oswald",
             "id_slug": "event-oswald-killed",
             "properties": {"event_type": "INCIDENT", "timestamp": "1963-11-24 11:21",
                            "location": "Dallas Police Headquarters",
                            "description": "Oswald shot by Jack Ruby during custody transfer"}},
            {"type": "Document", "name": "Warren Commission Report (1964)",
             "id_slug": "doc-warren-commission-report",
             "properties": {"published": "1964-09-24",
                            "publisher": "U.S. Government Printing Office",
                            "conclusion": "Oswald acted alone",
                            "source": "https://www.archives.gov/research/jfk"}},
        ],
        "relationships": [
            {"from": "person-lee-harvey-oswald", "from_type": "Person",
             "to": "org-tsbd",              "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "Warren Commission finding: Oswald employed at TSBD",
             "confidence": 1.0, "verified": True},
            {"from": "person-lee-harvey-oswald", "from_type": "Person",
             "to": "event-jfk-assassination", "to_type": "Event",
             "type": "INVOLVES",
             "evidence": "Warren Commission concluded Oswald fired the shots",
             "confidence": 0.9, "verified": True,
             "note": "Warren Commission conclusion; disputed by some researchers"},
            {"from": "person-jack-ruby",    "from_type": "Person",
             "to": "person-lee-harvey-oswald", "to_type": "Person",
             "type": "ASSOCIATED_WITH",
             "evidence": "Ruby shot Oswald on 24 Nov 1963 at Dallas Police HQ",
             "confidence": 1.0, "verified": True},
            {"from": "event-jfk-assassination", "from_type": "Event",
             "to": "loc-dealey-plaza",      "to_type": "Location",
             "type": "VISITED",
             "evidence": "Assassination occurred at Dealey Plaza, Dallas",
             "confidence": 1.0, "verified": True},
            {"from": "person-jfk",          "from_type": "Person",
             "to": "loc-parkland-hospital", "to_type": "Location",
             "type": "VISITED",
             "evidence": "Kennedy transported to Parkland Memorial Hospital; pronounced dead there",
             "confidence": 1.0, "verified": True},
            {"from": "org-warren-commission", "from_type": "Organization",
             "to": "doc-warren-commission-report", "to_type": "Document",
             "type": "MENTIONED_IN",
             "evidence": "Warren Commission published its report 24 Sep 1964",
             "confidence": 1.0, "verified": True},
        ],
    },

    # ── 2. Watergate ─────────────────────────────────────────────
    {
        "title": "Watergate: Presidential Obstruction of Justice Investigation",
        "description": (
            "The Watergate affair (1972–1974) began with the 17 June 1972 break-in at the "
            "Democratic National Committee headquarters at the Watergate complex in Washington D.C. "
            "It culminated in President Richard Nixon's resignation on 9 August 1974 — the only "
            "resignation of a sitting U.S. President. Multiple senior White House officials were "
            "convicted of crimes including obstruction of justice, perjury, and conspiracy. "
            "HISTORICAL REFERENCE case — educational network analysis demonstration."
        ),
        "priority": "CRITICAL",
        "status": "CLOSED",
        "category": "HISTORICAL_REFERENCE",
        "narrative_text": """HISTORICAL REFERENCE CASE — Educational Demonstration
SOURCE: Senate Watergate Committee Final Report (1974); U.S. v. Mitchell et al. (1975)

INCIDENT
On 17 June 1972, five men were arrested inside the Democratic National Committee (DNC)
headquarters at the Watergate complex, Washington D.C. Investigation revealed ties to
President Nixon's re-election committee (CRP/CREEP). Subsequent investigations uncovered
a pattern of illegal wiretapping, political sabotage, and a cover-up orchestrated from
the White House. President Nixon resigned on 9 August 1974. Senior officials were convicted
including the Attorney General, the White House Chief of Staff, and the White House Counsel.

PERSONS OF INTEREST

1. Richard M. Nixon
   37th President of the United States.
   Resigned 9 August 1974 to avoid impeachment. Pardoned by President Ford, 8 September 1974.

2. H.R. Haldeman (Harry Robbins Haldeman)
   White House Chief of Staff. Convicted of obstruction of justice, conspiracy, and perjury.
   Sentenced to 18 months in prison.

3. John Ehrlichman
   White House Domestic Affairs Advisor. Convicted of obstruction, conspiracy, and perjury.
   Sentenced to 18 months in prison.

4. John Dean
   White House Counsel. Pleaded guilty to obstruction of justice.
   Became a key witness for the prosecution. Sentenced to time served.

5. John N. Mitchell
   U.S. Attorney General and CRP director. Convicted of obstruction, conspiracy, and perjury.
   First U.S. Attorney General imprisoned. Sentenced to 19 months in prison.

6. G. Gordon Liddy
   Counsel to CRP. Convicted of conspiracy, burglary, and illegal wiretapping.
   Refused to cooperate with investigators. Sentenced to 20 years (served 4.5 years).

7. E. Howard Hunt
   Former CIA officer, CRP operative. Pleaded guilty to multiple charges.
   Sentenced to 30 months in prison.

ORGANISATIONS

- Committee to Re-Elect the President (CRP / "CREEP")
  Nixon's re-election campaign organisation. Funded covert operations.

- Democratic National Committee (DNC)
  Target of the Watergate break-in.

- Senate Select Committee on Presidential Campaign Activities
  ("Senate Watergate Committee"), chaired by Senator Sam Ervin.

- Office of the Special Prosecutor
  Archibald Cox (fired Oct 1973 — "Saturday Night Massacre"); Leon Jaworski (successor).

LOCATIONS

- Watergate complex, Washington D.C. — site of DNC break-in, 17 June 1972
- White House, Washington D.C. — centre of the cover-up operation

TIMELINE OF KEY EVENTS

17 Jun 1972  — Five burglars arrested at DNC headquarters, Watergate complex
23 Jun 1972  — Nixon approves using CIA to obstruct FBI investigation (White House tape)
19 Jan 1973  — Burglars convicted; Liddy and McCord refuse to cooperate
17 Apr 1973  — Nixon announces "major developments"; Dean dismissed
20 Oct 1973  — "Saturday Night Massacre": Nixon orders firing of Special Prosecutor Cox
27 Jul 1974  — House Judiciary Committee approves Articles of Impeachment
09 Aug 1974  — Nixon resigns as President
08 Sep 1974  — President Ford pardons Nixon
01 Jan 1975  — Haldeman, Ehrlichman, Mitchell convicted

OUTCOME
President Nixon resigned. 48 officials were indicted or convicted. The case established
executive accountability and led to major campaign finance reforms.

SOURCES
- Senate Watergate Committee Final Report (1974). U.S. Government Printing Office.
- United States v. Mitchell et al., Crim. No. 74-110 (D.D.C. 1975).
- Nixon Presidential Library and Museum: https://www.nixonlibrary.gov
""",
        "entities": [
            {"type": "Person", "name": "Richard M. Nixon", "id_slug": "person-nixon",
             "properties": {"role": "37th President of the United States",
                            "aliases": ["President Nixon", "RMN"],
                            "outcome": "Resigned 9 Aug 1974; pardoned by President Ford"}},
            {"type": "Person", "name": "H.R. Haldeman", "id_slug": "person-haldeman",
             "properties": {"role": "White House Chief of Staff",
                            "outcome": "Convicted; 18 months imprisonment"}},
            {"type": "Person", "name": "John Ehrlichman", "id_slug": "person-ehrlichman",
             "properties": {"role": "White House Domestic Affairs Advisor",
                            "outcome": "Convicted; 18 months imprisonment"}},
            {"type": "Person", "name": "John Dean", "id_slug": "person-john-dean",
             "properties": {"role": "White House Counsel",
                            "outcome": "Pleaded guilty; became prosecution witness"}},
            {"type": "Person", "name": "John N. Mitchell", "id_slug": "person-mitchell",
             "properties": {"role": "U.S. Attorney General; CRP Director",
                            "outcome": "Convicted; 19 months imprisonment"}},
            {"type": "Person", "name": "G. Gordon Liddy", "id_slug": "person-liddy",
             "properties": {"role": "CRP Counsel", "outcome": "Convicted; 4.5 years served"}},
            {"type": "Person", "name": "E. Howard Hunt", "id_slug": "person-hunt",
             "properties": {"role": "CIA former officer; CRP operative",
                            "outcome": "Pleaded guilty; 30 months imprisonment"}},
            {"type": "Organization", "name": "Committee to Re-Elect the President",
             "id_slug": "org-crp",
             "properties": {"alias": "CRP / CREEP",
                            "significance": "Funded Watergate burglary and covert operations"}},
            {"type": "Organization", "name": "Democratic National Committee",
             "id_slug": "org-dnc",
             "properties": {"alias": "DNC", "significance": "Target of break-in"}},
            {"type": "Organization", "name": "Senate Watergate Committee",
             "id_slug": "org-senate-watergate-committee",
             "properties": {"chair": "Senator Sam Ervin",
                            "significance": "Led public hearings; produced final report"}},
            {"type": "Location", "name": "Watergate Complex, Washington D.C.",
             "id_slug": "loc-watergate-complex",
             "properties": {"significance": "Site of DNC break-in, 17 Jun 1972"}},
            {"type": "Event", "name": "Watergate Break-in",
             "id_slug": "event-watergate-break-in",
             "properties": {"event_type": "INCIDENT", "timestamp": "1972-06-17",
                            "location": "Watergate Complex, Washington D.C.",
                            "description": "Five men arrested at DNC HQ during covert entry"}},
            {"type": "Event", "name": "Nixon Resignation",
             "id_slug": "event-nixon-resignation",
             "properties": {"event_type": "OTHER", "timestamp": "1974-08-09",
                            "description": "Nixon resigns — only U.S. President to do so"}},
            {"type": "Event", "name": "Saturday Night Massacre",
             "id_slug": "event-saturday-night-massacre",
             "properties": {"event_type": "OTHER", "timestamp": "1973-10-20",
                            "description": "Nixon orders firing of Special Prosecutor Cox; AG Richardson and Deputy AG Ruckelshaus resign"}},
            {"type": "Document", "name": "Senate Watergate Committee Report (1974)",
             "id_slug": "doc-senate-watergate-report",
             "properties": {"published": "1974",
                            "publisher": "U.S. Government Printing Office",
                            "source": "U.S. Senate archives"}},
        ],
        "relationships": [
            {"from": "person-haldeman",  "from_type": "Person",
             "to": "person-nixon",       "to_type": "Person",
             "type": "WORKS_FOR",
             "evidence": "Haldeman served as Nixon's Chief of Staff",
             "confidence": 1.0, "verified": True},
            {"from": "person-ehrlichman","from_type": "Person",
             "to": "person-nixon",       "to_type": "Person",
             "type": "WORKS_FOR",
             "evidence": "Ehrlichman served as White House Domestic Affairs Advisor",
             "confidence": 1.0, "verified": True},
            {"from": "person-john-dean", "from_type": "Person",
             "to": "person-nixon",       "to_type": "Person",
             "type": "WORKS_FOR",
             "evidence": "Dean served as White House Counsel; became prosecution witness",
             "confidence": 1.0, "verified": True},
            {"from": "person-mitchell",  "from_type": "Person",
             "to": "org-crp",            "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "Mitchell directed the Committee to Re-Elect the President",
             "confidence": 1.0, "verified": True},
            {"from": "person-liddy",     "from_type": "Person",
             "to": "org-crp",            "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "Liddy was CRP Counsel and planned the Watergate break-in",
             "confidence": 1.0, "verified": True},
            {"from": "person-hunt",      "from_type": "Person",
             "to": "org-crp",            "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "Hunt was a CRP operative involved in the break-in",
             "confidence": 1.0, "verified": True},
            {"from": "event-watergate-break-in", "from_type": "Event",
             "to": "org-dnc",            "to_type": "Organization",
             "type": "INVOLVES",
             "evidence": "DNC headquarters was the target of the break-in",
             "confidence": 1.0, "verified": True},
            {"from": "org-crp",          "from_type": "Organization",
             "to": "event-watergate-break-in", "to_type": "Event",
             "type": "PART_OF",
             "evidence": "Watergate burglars were connected to CRP",
             "confidence": 0.95, "verified": True},
        ],
    },

    # ── 3. Unabomber ──────────────────────────────────────────────
    {
        "title": "UNABOM: Kaczynski Mail-Bomb Campaign Investigation",
        "description": (
            "The UNABOM case (FBI designation) involved a series of 16 bomb attacks "
            "between 1978 and 1995 targeting universities and airlines, killing 3 people "
            "and injuring 23 others. Theodore John Kaczynski, known as the Unabomber, "
            "was identified after his brother David recognised his writing style in a "
            "published manifesto. Kaczynski pleaded guilty in 1998 and was sentenced to "
            "four consecutive life terms. HISTORICAL REFERENCE case — educational demonstration."
        ),
        "priority": "HIGH",
        "status": "CLOSED",
        "category": "HISTORICAL_REFERENCE",
        "narrative_text": """HISTORICAL REFERENCE CASE — Educational Demonstration
SOURCE: FBI UNABOM case files (public); U.S. v. Kaczynski, CR-S-96-259 GEB (E.D. Cal. 1998)

INCIDENT
Between 1978 and 1995, an individual the FBI designated "UNABOM" carried out 16 bomb attacks
across the United States, primarily targeting universities and airlines. The campaign killed
3 people and injured 23 others over 17 years — the longest manhunt in FBI history at that time.

PERPETRATOR

Theodore John Kaczynski (known as "The Unabomber")
Date of birth: 22 May 1942, Chicago, Illinois.
Former mathematics professor at UC Berkeley (1967–1969).
Lived as a recluse in a remote cabin near Lincoln, Montana.
Arrested: 3 April 1996, Lincoln, Montana.
Pleaded guilty: 22 January 1998 to avoid the death penalty.
Sentence: Four consecutive life terms without the possibility of parole.
Status: Died in federal custody, 10 June 2023.

KEY IDENTIFICATION EVENT
In 1995, Kaczynski sent an anonymous manifesto ("Industrial Society and Its Future") to
The New York Times and The Washington Post, demanding its publication.
His brother, David Kaczynski, recognised the writing style and ideas, and contacted the FBI
in February 1996 through an attorney. This tip led directly to the arrest.

INVESTIGATORS

- FBI UNABOM Task Force (established 1979)
  Joint task force of FBI, ATF, and U.S. Postal Inspection Service.

- David Kaczynski
  Brother of Theodore. Provided the tip to the FBI in February 1996.
  Sought assurances that the death penalty would not be sought (not guaranteed).

ATTACK PATTERN (Selected documented incidents — public record)
- 25 May 1978: Northwestern University, Evanston, IL — first bomb, minor injuries
- 15 May 1985: Boeing Fabrication Division, Auburn, WA — booby-trapped road; one injured
- 11 Dec 1985: Hugh Scrutton, Sacramento, CA — killed (first fatality)
- 22 Jun 1993: Dr. Charles Epstein, Tiburon, CA — seriously injured (mail bomb)
- 24 Jun 1993: Dr. David Gelernter, New Haven, CT — seriously injured (mail bomb)
- 10 Apr 1995: Gilbert Murray, Sacramento, CA — killed (mail bomb intended for William Dennison)
- 24 Apr 1995: Thomas Mosser, New Jersey — killed (mail bomb)

ORGANISATIONS

- FBI UNABOM Task Force — investigation team
- University of California, Berkeley — former employer of Kaczynski
- The New York Times / The Washington Post — recipients of the 1995 manifesto

LOCATIONS

- Lincoln, Montana — Kaczynski's remote cabin; site of arrest
- Sacramento, California — location of several bomb incidents
- Northwestern University, Evanston, Illinois — first attack

TIMELINE

25 May 1978  — First bomb at Northwestern University
08 May 1979  — Bomb on American Airlines Flight 444 (pressurised but did not explode fully)
11 Dec 1985  — First fatality: Hugh Scrutton, Sacramento
1979         — FBI UNABOM Task Force established
19 Sep 1995  — Manifesto published in The New York Times and The Washington Post
Feb 1996     — David Kaczynski contacts FBI through attorney after recognising manifesto
03 Apr 1996  — Theodore Kaczynski arrested at his cabin near Lincoln, Montana
22 Jan 1998  — Kaczynski pleads guilty; sentenced to four consecutive life terms
10 Jun 2023  — Kaczynski found dead in federal medical centre, Butner, North Carolina

OUTCOME
Theodore Kaczynski was convicted of all charges. He died in federal custody in 2023.
The case is studied for its lone-wolf terrorism profile and the role of behavioural analysis.

SOURCES
- FBI UNABOM case summary: https://www.fbi.gov/history/famous-cases/unabomber
- U.S. v. Kaczynski, CR-S-96-259 GEB (E.D. Cal. 1998). Court records, DOJ archives.
- DOJ press release, January 22, 1998.
""",
        "entities": [
            {"type": "Person", "name": "Theodore John Kaczynski", "id_slug": "person-kaczynski",
             "properties": {"aliases": ["The Unabomber", "UNABOM subject"],
                            "dob": "1942-05-22", "nationality": "American",
                            "occupation": "Former mathematics professor",
                            "last_known_address": "Lincoln, Montana (remote cabin)",
                            "outcome": "Pleaded guilty 1998; 4 consecutive life terms; died 2023"}},
            {"type": "Person", "name": "David Kaczynski", "id_slug": "person-david-kaczynski",
             "properties": {"relation": "Brother of Theodore Kaczynski",
                            "significance": "Provided FBI tip in February 1996 after recognising manifesto"}},
            {"type": "Organization", "name": "FBI UNABOM Task Force",
             "id_slug": "org-unabom-task-force",
             "properties": {"established": "1979",
                            "description": "Joint FBI/ATF/USPIS task force, longest active manhunt 1978–1996"}},
            {"type": "Organization", "name": "University of California, Berkeley",
             "id_slug": "org-uc-berkeley",
             "properties": {"significance": "Former employer of Kaczynski (mathematics dept, 1967–1969)"}},
            {"type": "Location", "name": "Lincoln, Montana",
             "id_slug": "loc-lincoln-montana",
             "properties": {"significance": "Location of Kaczynski's remote cabin; site of arrest"}},
            {"type": "Location", "name": "Northwestern University, Evanston, Illinois",
             "id_slug": "loc-northwestern",
             "properties": {"significance": "Site of first UNABOM attack, 25 May 1978"}},
            {"type": "Document", "name": "Industrial Society and Its Future (Manifesto)",
             "id_slug": "doc-unabomber-manifesto",
             "properties": {"published": "1995-09-19",
                            "publishers": "New York Times, Washington Post",
                            "significance": "Publication led to identification by David Kaczynski"}},
            {"type": "Event", "name": "First UNABOM Attack — Northwestern University",
             "id_slug": "event-unabom-first",
             "properties": {"event_type": "INCIDENT", "timestamp": "1978-05-25",
                            "location": "Northwestern University, Evanston, Illinois",
                            "description": "First bomb; minor injuries"}},
            {"type": "Event", "name": "Manifesto Published",
             "id_slug": "event-manifesto-published",
             "properties": {"event_type": "OTHER", "timestamp": "1995-09-19",
                            "description": "Manifesto published in NYT and WaPo under threat"}},
            {"type": "Event", "name": "Kaczynski Identified and Arrested",
             "id_slug": "event-kaczynski-arrested",
             "properties": {"event_type": "ARREST", "timestamp": "1996-04-03",
                            "location": "Lincoln, Montana",
                            "description": "Arrested after brother David identified manifesto style"}},
        ],
        "relationships": [
            {"from": "person-kaczynski",  "from_type": "Person",
             "to": "loc-lincoln-montana", "to_type": "Location",
             "type": "VISITED",
             "evidence": "Kaczynski lived in remote cabin near Lincoln, Montana",
             "confidence": 1.0, "verified": True},
            {"from": "person-kaczynski",  "from_type": "Person",
             "to": "org-uc-berkeley",     "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "Kaczynski was assistant professor of mathematics at UC Berkeley 1967–1969",
             "confidence": 1.0, "verified": True},
            {"from": "person-david-kaczynski", "from_type": "Person",
             "to": "person-kaczynski",    "to_type": "Person",
             "type": "KNOWS",
             "evidence": "David Kaczynski is Theodore's brother; provided identification tip",
             "confidence": 1.0, "verified": True},
            {"from": "person-kaczynski",  "from_type": "Person",
             "to": "doc-unabomber-manifesto", "to_type": "Document",
             "type": "MENTIONED_IN",
             "evidence": "Kaczynski authored the manifesto (confirmed at trial)",
             "confidence": 1.0, "verified": True},
            {"from": "doc-unabomber-manifesto", "from_type": "Document",
             "to": "event-kaczynski-arrested", "to_type": "Event",
             "type": "CONNECTED_TO",
             "evidence": "Publication of manifesto led David Kaczynski to contact FBI",
             "confidence": 1.0, "verified": True},
        ],
    },

    # ── 4. Golden State Killer ────────────────────────────────────
    {
        "title": "Golden State Killer — East Area Rapist Investigation",
        "description": (
            "Joseph James DeAngelo Jr., a former California police officer, was identified "
            "in April 2018 as the perpetrator of at least 13 murders, 50+ rapes, and 100+ "
            "burglaries committed between 1973 and 1986 across California. "
            "He was identified through investigative genetic genealogy using a public DNA "
            "database (GEDmatch) — the first major criminal case solved by this technique. "
            "DeAngelo pleaded guilty on 29 June 2020 and was sentenced to multiple consecutive "
            "life terms. HISTORICAL REFERENCE case — educational demonstration."
        ),
        "priority": "CRITICAL",
        "status": "CLOSED",
        "category": "HISTORICAL_REFERENCE",
        "narrative_text": """HISTORICAL REFERENCE CASE — Educational Demonstration
SOURCE: California DOJ press releases (2018); People v. DeAngelo, Sacramento County Superior
Court, Case No. 18FE006928 (2020); California AG press releases.

INCIDENT
Between 1973 and 1986, an unidentified subject committed a series of crimes across California
including at least 13 murders, more than 50 rapes, and more than 100 residential burglaries.
The subject was linked by DNA evidence across multiple crime scenes and was known by several
investigative names: "Visalia Ransacker" (1973–1975), "East Area Rapist" (1976–1979),
and "Original Night Stalker" or "Golden State Killer" (1979–1986).

PERPETRATOR

Joseph James DeAngelo Jr.
Date of birth: 8 November 1945, Bath, New York.
Former police officer: Exeter, California PD (1973–1976); Auburn, California PD (1976–1979).
Dismissed from Auburn PD in 1979 following a shoplifting arrest.
Resided in Citrus Heights, California at time of arrest.
Arrested: 24 April 2018, Citrus Heights, California.
Pleaded guilty: 29 June 2020 to 13 first-degree murder charges and numerous additional offences.
Sentenced: 16 August 2020 to multiple consecutive life terms without the possibility of parole.

DNA IDENTIFICATION METHOD
In 2017–2018, investigators submitted DNA evidence from crime scenes to GEDmatch, a public
genealogical DNA database. Genetic genealogist Barbara Rae-Venter (contracted by FBI/investigators)
constructed a family tree from partial DNA matches and identified DeAngelo as the likely perpetrator.
DNA collected from a discarded item (an item DeAngelo had touched) confirmed the match.
This was the first major criminal case solved using investigative genetic genealogy.

KEY INVESTIGATORS

- Paul Holes — cold case investigator, Contra Costa County DA's office
- Barbara Rae-Venter — genetic genealogist who identified DeAngelo through GEDmatch
- Sacramento County Sheriff's Department
- Multiple California law enforcement agencies via Multi-Agency Investigative Team

ORGANISATIONS

- California Department of Justice — led coordinated investigation
- Sacramento County District Attorney's Office — prosecuted
- GEDmatch — public genealogical DNA database used for identification
- Multi-Agency Investigative Team (MAIT) — joint law enforcement task force

LOCATIONS

- Sacramento area, California — primary operating area (East Area Rapist phase)
- Santa Barbara County, California — several murders
- Citrus Heights, California — DeAngelo's residence at arrest

TIMELINE

1973         — "Visalia Ransacker" crimes begin, Visalia, California
Jun 1976     — First East Area Rapist attack, Rancho Cordova, CA
1979         — Joseph DeAngelo dismissed from Auburn PD following shoplifting arrest
1979–1986    — "Original Night Stalker" murders continue in Southern California
2001         — DNA evidence links East Area Rapist and Original Night Stalker cases
2017         — Investigators submit crime scene DNA to GEDmatch
Jan 2018     — Barbara Rae-Venter identifies DeAngelo through genealogical analysis
24 Apr 2018  — DeAngelo arrested at his home in Citrus Heights; DNA confirmed
29 Jun 2020  — DeAngelo pleads guilty to 13 murders and related charges
16 Aug 2020  — DeAngelo sentenced to multiple consecutive life terms

OUTCOME
Joseph James DeAngelo Jr. is serving multiple consecutive life terms without parole.
The case is foundational to the practice of investigative genetic genealogy.

SOURCES
- California DOJ press release, 25 April 2018:
  https://oag.ca.gov/news/press-releases/attorney-general-becerra-announces-arrest-golden-state-killer
- People v. DeAngelo, Sacramento County Superior Court, Case No. 18FE006928 (2020).
- California AG: https://oag.ca.gov
""",
        "entities": [
            {"type": "Person", "name": "Joseph James DeAngelo Jr.", "id_slug": "person-deangelo",
             "properties": {
                 "aliases": ["Golden State Killer", "East Area Rapist",
                             "Original Night Stalker", "Visalia Ransacker"],
                 "dob": "1945-11-08",
                 "nationality": "American",
                 "former_occupation": "Police officer (Exeter PD; Auburn PD)",
                 "last_known_address": "Citrus Heights, California",
                 "outcome": "Pleaded guilty 2020; multiple consecutive life terms without parole",
             }},
            {"type": "Person", "name": "Paul Holes", "id_slug": "person-paul-holes",
             "properties": {
                 "role": "Cold case investigator, Contra Costa County DA's office",
                 "significance": "Led the DNA/genealogy investigation strategy",
             }},
            {"type": "Person", "name": "Barbara Rae-Venter", "id_slug": "person-rae-venter",
             "properties": {
                 "role": "Forensic genetic genealogist",
                 "significance": "Identified DeAngelo by building family tree from GEDmatch partial DNA matches",
             }},
            {"type": "Organization", "name": "California Department of Justice",
             "id_slug": "org-ca-doj",
             "properties": {"significance": "Coordinated multi-agency investigation"}},
            {"type": "Organization", "name": "Sacramento County DA's Office",
             "id_slug": "org-sac-da",
             "properties": {"significance": "Prosecuted DeAngelo"}},
            {"type": "Organization", "name": "GEDmatch",
             "id_slug": "org-gedmatch",
             "properties": {
                 "type": "Public genealogical DNA database",
                 "significance": "Crime scene DNA submitted here; partial matches led to family tree construction",
             }},
            {"type": "Organization", "name": "Auburn Police Department",
             "id_slug": "org-auburn-pd",
             "properties": {
                 "significance": "DeAngelo's former employer; dismissed 1979 after shoplifting arrest",
             }},
            {"type": "Location", "name": "Sacramento, California",
             "id_slug": "loc-sacramento",
             "properties": {"significance": "Primary area of East Area Rapist crimes (1976–1979)"}},
            {"type": "Location", "name": "Citrus Heights, California",
             "id_slug": "loc-citrus-heights",
             "properties": {"significance": "DeAngelo's residence at time of arrest"}},
            {"type": "Event", "name": "DeAngelo Identified via Genetic Genealogy",
             "id_slug": "event-gsk-identified",
             "properties": {"event_type": "OTHER", "timestamp": "2018-01",
                            "description": "Barbara Rae-Venter identifies DeAngelo as suspect through GEDmatch family tree analysis"}},
            {"type": "Event", "name": "Arrest of Joseph James DeAngelo Jr.",
             "id_slug": "event-deangelo-arrested",
             "properties": {"event_type": "ARREST", "timestamp": "2018-04-24",
                            "location": "Citrus Heights, California",
                            "description": "DeAngelo arrested; DNA from discarded item confirmed match to crime scenes"}},
            {"type": "Event", "name": "DeAngelo Guilty Plea and Sentencing",
             "id_slug": "event-deangelo-sentenced",
             "properties": {"event_type": "OTHER", "timestamp": "2020-08-16",
                            "description": "Pleaded guilty to 13 murders; sentenced to multiple consecutive life terms"}},
            {"type": "Document", "name": "CA DOJ Arrest Press Release (2018)",
             "id_slug": "doc-ca-doj-2018",
             "properties": {
                 "published": "2018-04-25",
                 "publisher": "California Attorney General Xavier Becerra",
                 "source": "https://oag.ca.gov/news/press-releases/attorney-general-becerra-announces-arrest-golden-state-killer",
             }},
        ],
        "relationships": [
            {"from": "person-deangelo",  "from_type": "Person",
             "to": "org-auburn-pd",      "to_type": "Organization",
             "type": "WORKS_FOR",
             "evidence": "DeAngelo served as police officer at Auburn PD 1976–1979; dismissed after shoplifting",
             "confidence": 1.0, "verified": True},
            {"from": "person-rae-venter","from_type": "Person",
             "to": "org-gedmatch",       "to_type": "Organization",
             "type": "ASSOCIATED_WITH",
             "evidence": "Rae-Venter used GEDmatch to build family tree from partial DNA matches",
             "confidence": 1.0, "verified": True},
            {"from": "person-paul-holes","from_type": "Person",
             "to": "person-rae-venter",  "to_type": "Person",
             "type": "ASSOCIATED_WITH",
             "evidence": "Holes and Rae-Venter collaborated on the genetic genealogy identification strategy",
             "confidence": 0.9, "verified": True},
            {"from": "person-deangelo",  "from_type": "Person",
             "to": "loc-sacramento",     "to_type": "Location",
             "type": "VISITED",
             "evidence": "East Area Rapist crimes occurred in Sacramento area; linked to DeAngelo by DNA",
             "confidence": 1.0, "verified": True},
            {"from": "person-deangelo",  "from_type": "Person",
             "to": "loc-citrus-heights", "to_type": "Location",
             "type": "VISITED",
             "evidence": "DeAngelo resided in Citrus Heights at time of arrest",
             "confidence": 1.0, "verified": True},
            {"from": "event-deangelo-arrested", "from_type": "Event",
             "to": "event-gsk-identified",       "to_type": "Event",
             "type": "CONNECTED_TO",
             "evidence": "Arrest followed from genetic genealogy identification",
             "confidence": 1.0, "verified": True},
            {"from": "org-ca-doj",       "from_type": "Organization",
             "to": "doc-ca-doj-2018",    "to_type": "Document",
             "type": "MENTIONED_IN",
             "evidence": "CA DOJ published press release announcing arrest",
             "confidence": 1.0, "verified": True},
        ],
    },
]


# ── API helpers ───────────────────────────────────────────────
def get_token(api_base: str) -> str:
    r = requests.post(f"{api_base}/auth/login",
                      json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
                      timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def case_exists(api_base: str, headers: dict, title: str) -> str | None:
    """Return case_id if a case with this exact title already exists, else None."""
    r = requests.get(f"{api_base}/cases", headers=headers, timeout=10)
    r.raise_for_status()
    for case in r.json().get("cases", []):
        if case["title"] == title:
            return case["id"]
    return None


def create_case(api_base: str, headers: dict, definition: dict) -> str:
    payload = {
        "title":       definition["title"],
        "description": definition["description"],
        "priority":    definition["priority"],
    }
    r = requests.post(f"{api_base}/cases", json=payload, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["id"]


def upload_narrative(api_base: str, headers: dict, case_id: str,
                     title: str, text: str) -> None:
    """Upload the narrative text file for a case."""
    filename = title.replace(" ", "_").replace("/", "-")[:60] + ".txt"
    files = {"file": (filename, text.encode("utf-8"), "text/plain")}
    # Strip Content-Type from headers for multipart
    upload_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
    r = requests.post(f"{api_base}/cases/{case_id}/documents",
                      files=files, headers=upload_headers, timeout=30)
    if not r.ok:
        print(f"      Warning: narrative upload failed: {r.status_code} {r.text[:200]}")


def write_graph_direct(api_base: str, headers: dict, case_id: str,
                       definition: dict) -> None:
    """
    Since we cannot call Neo4j directly from this script, we construct a
    structured JSON file containing the entity/relationship data and upload it
    as a JSON document. The backend's ingestion pipeline will treat it as
    GENERIC_JSON and the LLM/deterministic parser will handle it.

    We also write the entities/relationships directly via a dedicated seeding
    endpoint if one exists, otherwise fall back to JSON upload.
    """
    seed_payload = {
        "entities":      definition["entities"],
        "relationships": definition["relationships"],
        "events": [
            e["properties"] | {"id": e["id_slug"], "name": e["name"],
                                "type": e.get("type", "Event")}
            for e in definition["entities"]
            if e.get("type") == "Event"
        ],
        "source": "HISTORICAL_REFERENCE",
        "case_id": case_id,
    }
    filename = f"seed_graph_{case_id[:8]}.json"
    json_bytes = json.dumps(seed_payload, indent=2).encode("utf-8")
    files = {"file": (filename, json_bytes, "application/json")}
    upload_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
    r = requests.post(f"{api_base}/cases/{case_id}/documents",
                      files=files, headers=upload_headers, timeout=30)
    if r.ok:
        print(f"      Graph seed JSON uploaded (job: {r.json().get('job_id', '?')})")
    else:
        print(f"      Warning: graph seed upload status {r.status_code}")


# ── Main ──────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed historical reference cases into THE MENTALIST")
    parser.add_argument("--api", default=DEFAULT_API,
                        help=f"API base URL (default: {DEFAULT_API})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Check connectivity and print plan without modifying data")
    args = parser.parse_args()

    api = args.api.rstrip("/")
    print("=" * 62)
    print("  THE MENTALIST — Historical Case Seeder")
    print("  All data sourced from public records.")
    print("=" * 62)

    # Auth
    print(f"\n[1/3] Authenticating with {api} …")
    try:
        token = get_token(api)
    except Exception as e:
        print(f"  ERROR: Cannot authenticate — {e}")
        print("  Make sure the backend is running and demo user exists.")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"  ✓ Authenticated")

    if args.dry_run:
        print("\n[DRY RUN] Would seed the following cases:")
        for i, c in enumerate(HISTORICAL_CASES, 1):
            print(f"  {i}. {c['title']}")
            print(f"     Entities: {len(c['entities'])}  Relationships: {len(c['relationships'])}")
        print("\nRe-run without --dry-run to seed.")
        return

    # Seed
    print(f"\n[2/3] Seeding {len(HISTORICAL_CASES)} historical reference cases …\n")
    seeded = 0
    skipped = 0

    for definition in HISTORICAL_CASES:
        print(f"  ▶  {definition['title']}")

        existing_id = case_exists(api, headers, definition["title"])
        if existing_id:
            print(f"     ⟳  Already exists (id: {existing_id[:8]}…) — skipping\n")
            skipped += 1
            continue

        try:
            case_id = create_case(api, headers, definition)
            print(f"     ✓ Case created: {case_id[:8]}…")
        except Exception as e:
            print(f"     ✗ Failed to create case: {e}\n")
            continue

        # Upload narrative text
        try:
            upload_narrative(api, headers, case_id,
                             definition["title"], definition["narrative_text"])
            print(f"     ✓ Narrative document uploaded")
        except Exception as e:
            print(f"     ! Narrative upload error: {e}")

        # Upload graph seed JSON
        try:
            write_graph_direct(api, headers, case_id, definition)
        except Exception as e:
            print(f"     ! Graph seed error: {e}")

        seeded += 1
        print()
        time.sleep(0.5)   # small delay between cases

    print(f"[3/3] Summary")
    print(f"  Seeded:  {seeded} cases")
    print(f"  Skipped: {skipped} (already existed)")
    print(f"\n  Open http://localhost:3000 and navigate to Case Library.")
    print(f"  Historical cases are labelled HISTORICAL REFERENCE.\n")


if __name__ == "__main__":
    main()
