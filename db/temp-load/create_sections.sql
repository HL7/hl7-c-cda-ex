insert into sections (id,name,section_type,narrative,created_at,updated_at)
  values (1,'Header','hdr','','2016-09-01','2016-09-01'),
    (2,'Care Plan', 'doc','','2016-09-01','2016-09-01'),
    (3,'CCD','doc','','2016-09-01','2016-09-01'),
    (4,'Allergies','sect','##Allergies and Intolerances Section Examples from C-CDA','2016-09-01','2016-09-01'),
    (5,'Problem','sect','##Problem Section Examples from C-CDA','2016-09-01','2016-09-01');

insert into examples (id,section_id,name,comments,custodian,keywords,status,
                      example,created_at,updated_at)
  values (1,4,'Allergy to specific substance','This is an example of an allergy to a specific substance (cat hair) using UNII as terminology with information on both allergic reaction and reaction severity. See DSTU 219 for update regarding act/cod','John D''Amore jdamore@diameterhealth.com (GitHub: jddamore)','{substance,allergies,allergy}','pend',
$$
<section>
	<templateId root="2.16.840.1.113883.10.20.22.2.6.1"/>
	<!-- Allergies (entries required) section template -->
	<code code="48765-2" codeSystem="2.16.840.1.113883.6.1"/>
	<title>Allergies, Adverse Reactions and Alerts</title>
	<text>
		<table>
			<thead>
				<tr>
					<th>Allergen</th>
					<th>Reaction</th>
					<th>Reaction Severity</th>
					<th>Documentation Date</th>
					<th>Start Date</th>
				</tr>
			</thead>
			<tbody>
				<tr ID="allergy1">
					<td ID="allergy1allergen">Cat hair</td>
					<td ID="allergy1reaction">Rash</td>
					<td ID="allergy1reactionseverity">Moderate</td>
					<td>Jan 4 2014</td>
					<td>1998</td>
				</tr>
			</tbody>
		</table>
	</text>
	<entry typeCode="DRIV">
		<act classCode="ACT" moodCode="EVN">
			<!-- ** Allergy problem act ** -->
			<templateId root="2.16.840.1.113883.10.20.22.4.30"/>
			<id root="4a2ac5fc-0c85-4223-baee-c2e254803974" />
			<code code="CONC" codeSystem="2.16.840.1.113883.5.6"/>
			<statusCode code="active"/>
			<!-- This is the time stamp for when the allergy was first documented as a concern-->
			<effectiveTime>
				<low value="20140104123506+0500"/>
			</effectiveTime>
			<entryRelationship typeCode="SUBJ">
				<observation classCode="OBS" moodCode="EVN">
					<!-- allergy observation template -->
					<templateId root="2.16.840.1.113883.10.20.22.4.7"/>
					<id root="4a2ac5fc-0c85-4223-baee-c2e254803974"/>
					<code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
					<statusCode code="completed"/>
					<!-- This is the time stamp for the biological onset of the allergy. -->
					<!-- Just the year is shown since a specific month and date was not reported -->
					<effectiveTime>
						<low value="1998"/>
					</effectiveTime>
					<!-- This specifies that the allergy is to a substance (cat hair) in contrast to other allergies (drug) -->
					<value xsi:type="CD" code="419199007" displayName="allergy to substance" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT"></value>
					<participant typeCode="CSM">
						<participantRole classCode="MANU">
							<playingEntity classCode="MMAT">
								<!-- UNII is the preferred in C-CDA R 1.1 although per DSTU 381 SNOMED is also allowed in code element -->
								<code code="1564HD0N96" displayName="Cat hair" codeSystem="2.16.840.1.113883.4.9" codeSystemName="UNII">
									<originalText>
										<reference value="#allergy1allergen"/>
									</originalText>
								</code>
							</playingEntity>
						</participantRole>
					</participant>
					<entryRelationship typeCode="MFST" inversionInd="true">
						<observation classCode="OBS" moodCode="EVN">
							<!-- Reaction Observation template -->
							<templateId root="2.16.840.1.113883.10.20.22.4.9"/>
							<id root="0506c036-adfb-4e6e-b9e1-eea76177ead5"/>
							<!-- This code was not specified in C-CDA IG 1.1 although using ASSERTION aligns with C-CDA IG 2.0-->
							<code code="ASSERTION" codeSystem="2.16.840.1.113883.5.4"/>
							<text>
								<reference value="#allergy1reaction"/>
							</text>
							<statusCode code="completed"/>
							<effectiveTime>
								<low value="1998"/>
							</effectiveTime>
							<value xsi:type="CD" code="64144002" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT" displayName="Rash"/>
							<entryRelationship typeCode="SUBJ" inversionInd="true">
								<observation classCode="OBS" moodCode="EVN">
									<!-- Severity Observation template -->
									<templateId root="2.16.840.1.113883.10.20.22.4.8"/>
									<code code="SEV" codeSystem="2.16.840.1.113883.5.4" codeSystemName="ActCode"/>
									<text>
										<reference value="#allergy1reactionseverity"/>
									</text>
									<statusCode code="completed"/>
									<value xsi:type="CD" code="6736007" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT" displayName="moderate"/>
								</observation>
							</entryRelationship>
						</observation>
					</entryRelationship>
					<!-- Note that severity may also be specified for observation and has SHOULD conformance in C-CDA 1.1 -->
					<!-- We have only included allergy severity to a specific reaction as outlined in HL7 Patient Care Committee materials-->
				</observation>
			</entryRelationship>
		</act>
	</entry>
</section>
$$,'2016-09-01','2016-09-01'),
    (2,4,'No Known Allergies','','','{unknown,allergies,allergy}','pend',
     '','2016-09-01','2016-09-01');

INSERT INTO approvals (example_id,committee,approved,date,comment)
  VALUES (1,'Example Task Force', TRUE ,'2014-10-4',null),
    (1,'SDWG',FALSE ,null,'Withdrawn from consideration since not clinically relevant.');