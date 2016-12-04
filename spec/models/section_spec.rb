require 'rails_helper'

RSpec.describe Section, type: :model do
  context 'creation' do
    subject { FactoryGirl.build(:section) }
    it      { should be_valid }
  end

  context 'validation' do
    subject { FactoryGirl.build(:section) }

    it { should fail_with_null(:name) }
    it { should fail_with_null(:section_type) }
    it { should pass_with_null(:narrative) }

  end
end
