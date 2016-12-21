require 'rails_helper'

RSpec.describe Example, type: :model do
  let(:section) { FactoryGirl.build(:section) }

  context 'creation' do
    subject { FactoryGirl.build(:example, section: section) }
    it      { should be_valid }
  end

  context 'validation' do
    subject { FactoryGirl.build(:example, section: section) }

    it { should fail_with_null(:name) }
    it { should fail_with_null(:section) }
    it { should pass_with_null(:comments) }
    it { should pass_with_null(:custodian) }
    it { should pass_with_null(:validation) }
    it { should pass_with_null(:keywords) }
    it { should pass_with_null(:full_sample) }
    it { should fail_with_null(:status) }
    it { should pass_with_null(:oids) }
    it { should pass_with_null(:example) }
    it { should pass_with_null(:example_url) }
  end

  context 'query' do
    before(:each) do
      @section_1 = FactoryGirl.create(:section)
      @section_2 = FactoryGirl.create(:section)
      @ex_1 = FactoryGirl.create(:example_search_1, section: @section_1)
      @ex_2 = FactoryGirl.create(:example_search_2, section: @section_1)
      @ex_3 = FactoryGirl.create(:example_search_3, section: @section_2)
    end

    it 'should find all with no criteria' do
      query = SearchCriteria.new()
      found = Example.query(query)
      expect(found.count).to eq(3)
    end

    it 'should find by status' do
      query = SearchCriteria.new(status: ['draft'])
      found = Example.query(query)
      expect(found.count).to eq(0)

      query = SearchCriteria.new(status: ['wthd'])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_3.id)

      query = SearchCriteria.new(status: ['pend'])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)
    end

    it 'should find with multiple statuses' do
      query = SearchCriteria.new(status: ['wthd', 'pend'])
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_3.id, @ex_2.id].sort)
    end

    it 'should find by section' do
      query = SearchCriteria.new(section_ids: [@section_1.id])
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_2.id].sort)

      query = SearchCriteria.new(section_ids: [@section_2.id])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_3.id)
    end

    it 'should with multiple sections' do
      query = SearchCriteria.new(section_ids: [@section_1.id, @section_2.id])
      found = Example.query(query)
      expect(found.count).to eq(3)
    end

    it 'should find by keyword' do
      query = SearchCriteria.new(search_text: 'ribeye')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_3.id)

      query = SearchCriteria.new(search_text: 'bacon')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_2.id].sort)

      query = SearchCriteria.new(search_text: 'pork')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_3.id, @ex_2.id].sort)
    end

    it 'should find with multiple keywords' do
      query = SearchCriteria.new(search_text: 'custard ham')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_3.id, @ex_2.id].sort)

      query = SearchCriteria.new(search_text: 'bacon ribeye')
      found = Example.query(query)
      expect(found.count).to eq(3)
    end

    it 'should find by custodian' do
      query = SearchCriteria.new(search_text: 'john')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_1.id)

      query = SearchCriteria.new(search_text: 'cecilia')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)

      query = SearchCriteria.new(search_text: 'dogg')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_3.id, @ex_2.id].sort)
    end

    it 'should find by word in comment' do
      query = SearchCriteria.new(search_text: 'lunch')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)

      query = SearchCriteria.new(search_text: 'supper')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_3.id)
    end

    it 'should find by word in name' do
      query = SearchCriteria.new(search_text: 'epinephrine')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)

      query = SearchCriteria.new(search_text: 'medication')
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_3.id)

      query = SearchCriteria.new(search_text: 'allergy')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_2.id].sort)
    end

    it 'should allow search words that have quotes' do
      query = SearchCriteria.new(search_text: "d'amore")
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_1.id)
    end

    it 'should find by certification' do
      query = SearchCriteria.new()
      found = Example.query(query)
      expect(found.count).to eq(3)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_2.id, @ex_3.id].sort)

      query = SearchCriteria.new(search_certification: '1')
      found = Example.query(query)
      expect(found.count).to eq(2)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_3.id].sort)

      query = SearchCriteria.new(search_certification: '0')
      found = Example.query(query)
      expect(found.count).to eq(3)
      expect((found.collect {|x| x.id}).sort).to eq([@ex_1.id, @ex_2.id, @ex_3.id].sort)
    end

    it 'should find with a combination of criteria' do
      query = SearchCriteria.new(search_text: 'epinephrine', section_ids: [@section_1.id],
                                 status: [''])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)

      query = SearchCriteria.new(section_ids: [@section_1.id], status: ['app'])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_1.id)

      query = SearchCriteria.new(search_text: 'epinephrine', section_ids: [@section_1.id],
                                 status: ['pend'])
      found = Example.query(query)
      expect(found.count).to eq(1)
      expect(found[0].id).to eq(@ex_2.id)

      query = SearchCriteria.new(search_text: 'epinephrine', section_ids: [@section_1.id],
                                 status: ['app'])
      found = Example.query(query)
      expect(found.count).to eq(0)

      query = SearchCriteria.new(search_text: 'epinephrine', section_ids: [@section_2.id],
                                 status: ['app'])
      found = Example.query(query)
      expect(found.count).to eq(0)
    end
  end
end
