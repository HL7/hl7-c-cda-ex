class Example < ActiveRecord::Base
  belongs_to :section

  has_many :approvals
end
