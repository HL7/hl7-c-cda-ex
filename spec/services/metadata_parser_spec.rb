require 'rails_helper'

describe MetadataParser do
  RAW_METADATA = <<-ENDDATA
##Approval Status 

* Approval Status: Approved
* Example Task Force: 1/30/2014
* SDWG: 2/6/2014


###C-CDA 2.1 Example: 

* 2.16.840.1.113883.10.20.22.2.5.1:2015-08-01

###Reference to full CDA sample:
* Problems in empty CCD


###Validation location

* [SITE](https://sitenv.org/c-cda-validator)


###Comments

* This is an example of no information available for problems.

###Certification

* ONC
* CSA

###Custodian

* Brett Marquard, brett@riverrockassociates.com (GitHub: brettmarquard)
###Keywords

* null section, no information section
  ENDDATA

  context 'parsing empty metadata' do
    it 'should build a default metadata object' do
      expect(MetadataParser.parse('')).to be_a(ExampleMetadata)
    end

    it 'should set the default status to Pending' do
      expect(MetadataParser.parse('').status).to eq 'pend'
    end

    it 'should set the default certification to false' do
      expect(MetadataParser.parse('').onc_certification).to be false
    end

    it 'should set other attributes to nil' do
      temp = MetadataParser.parse('')
      expect(temp.comments).to be_nil
      expect(temp.custodian).to be_nil
      expect(temp.validation).to be_nil
      expect(temp.keywords).to be_nil
      expect(temp.full_sample).to be_nil
      expect(temp.oids).to be_nil
      expect(temp.approvals).to be_nil
    end
  end

  context 'parsing valid metadata' do
    it 'should correctly populate status' do
      expect(MetadataParser.parse(RAW_METADATA).status).to eq 'app'
    end

    it 'should populate certification' do
      expect(MetadataParser.parse(RAW_METADATA).onc_certification).to be true
    end
  end
end