class Approval < ActiveRecord::Base
  belongs_to :example

  validates :example, presence: true
  validates :committee, presence: true
  validates :approved, inclusion: {in: [true, false]}
end