require 'rails_helper'

RSpec.describe RepoMessage, type: :model do
  context 'creation' do
    subject { FactoryGirl.build(:repo_message) }
    it      { should be_valid }
  end

  context 'validation' do
    subject { FactoryGirl.build(:repo_message) }

    it { should pass_with_null(:description) }
    it { should pass_with_null(:action) }
    it { should pass_with_null(:body) }
    it { should fail_with_null(:status) }
    it { should pass_with_null(:repo_source) }
    it { should pass_with_null(:new) }
    it { should pass_with_null(:new_status) }
    it { should pass_with_null(:modified) }
    it { should pass_with_null(:modified_status) }
  end
end
