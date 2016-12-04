class Section < ActiveRecord::Base
  has_many :examples

  validates :name, presence: true
  validates :section_type, presence: true
end
