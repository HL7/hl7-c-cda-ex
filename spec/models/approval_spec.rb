require 'rails_helper'

RSpec.describe Approval, type: :model do
  let(:section) { FactoryGirl.build(:section) }
  let(:example) { FactoryGirl.build(:example, section: section) }

  context 'creation' do
    subject { FactoryGirl.build(:approval, example: example) }
    it      { should be_valid }
  end

  context 'validation' do
    subject { FactoryGirl.build(:approval, example: example) }
#
    it { should fail_with_null(:example) }
    it { should fail_with_null(:committee) }
    it { should fail_with_null(:approved) }
    it { should pass_with_null(:date) }
    it { should pass_with_null(:comment) }
  end
end