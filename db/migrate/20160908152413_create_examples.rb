class CreateExamples < ActiveRecord::Migration
  def change
    create_table :examples do |t|
      t.references :section, null: false, index: true
      t.string     :name, limit: 120
      t.string     :comments
      t.string     :custodian
      t.string     :validation
      t.string     :keywords
      t.string     :full_sample
      t.string     :status, limit: 20, null: false
      t.string     :oids, array: true
      t.text       :example
      t.string     :example_url

      t.timestamps null: false
    end

    create_table :approvals do |t|
      t.references :example, null: false, index: true
      t.string     :committee, null: false
      t.boolean    :approved, null: false, default: false
      t.date       :date
      t.text       :comment
    end
  end
end
