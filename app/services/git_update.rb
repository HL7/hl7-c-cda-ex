class GitUpdate
  def self.process!(github_message)
    unless github_message.status == 'unk' || github_message.status == 'comp'
      new(github_message).run
    end
  end

  def run
    @commit_message.status = 'proc'
    @commit_message.save!

    process_adds
    process_mods

    @commit_message.status = 'comp'
    @commit_message.save!
  end

  def process_adds
    @commit_message.new && @commit_message.new.each_index do |indx|
      unless @commit_message.new_status[indx] == 'comp'
        @commit_message.new_status[indx] = 'proc'
        @commit_message.save!
        if ApplyUpdate.process!(@commit_message.repo_source, @commit_message.new[indx])
          @commit_message.new_status[indx] = 'comp'
        else
          @commit_message.new_status[indx] = 'err'
        end
      end
    end
  end

  def process_mods
    @commit_message.modified && @commit_message.modified.each_index do |indx|
      unless @commit_message.modified_status[indx] == 'comp'
        @commit_message.modified_status[indx] = 'proc'
        @commit_message.save!
        if ApplyUpdate.process!(@commit_message.repo_source, @commit_message.modified[indx])
          @commit_message.modified_status[indx] = 'comp'
        else
          @commit_message.modified_status[indx] = 'err'
        end
      end
    end
  end

  private
  def initialize(github_commit)
    @commit_message = github_commit
  end
end