class Section < ActiveRecord::Base
  has_many :examples

  scope :ordered_by_name, -> { order(name: :asc) }

  validates :name, presence: true
  validates :section_type, presence: true
end
