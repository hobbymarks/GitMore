/*
Copyright © 2022 hobbymarks ihobbymarks@gmail.com
*/
package cmd

import (
	"errors"
	"os"
	"path/filepath"

	"github.com/hobbymarks/giat/pb"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"
)

var version = "0.0.0"

var GiatRecordPath string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:     "giat",
	Version: version,
	Short:   "unify local GitRepoDirecotry name",
	Long: `A tool for changing local GitRepoDirectory name to GitRepoName@OrganizationName.
For example:
	ProjectDir ==> GitRepoName@OrganizationName
	GiatLocalDir ==> giat@hobbymarks
	...
`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	homeDir, err := os.UserHomeDir() //get home dir
	if err != nil {
		log.Fatal(err)
	}
	GiatRecordPath = filepath.Join(homeDir, ".giat")
	if _, err := os.Lstat(GiatRecordPath); errors.Is(err, os.ErrNotExist) {
		if err := os.Mkdir(GiatRecordPath, os.ModePerm); err != nil {
			log.Fatal(err)
		}
	}
	GiatRecordPath = filepath.Join(GiatRecordPath, "giat.rd")
	if _, err := os.Stat(GiatRecordPath); err != nil { //if not exist then create
		giatrds := pb.GiatRecords{}
		if data, err := proto.Marshal(&giatrds); err != nil {
			log.Fatal(err)
		} else {
			if err := os.WriteFile(GiatRecordPath, data, 0644); err != nil {
				log.Fatal(err)
			}
		}
	}
}

func FreezeGitDir(dirPath string) error {
	if data, err := os.ReadFile(GiatRecordPath); err != nil {
		log.Error(err)
		return err
	} else {
		giatrds := pb.GiatRecords{}
		if err := proto.Unmarshal(data, &giatrds); err != nil {
			log.Error(err)
			return err
		}
		fp := filepath.Join(dirPath, ".git", "config")
		if rURL, _, err := DecodeGitConfig(fp); err != nil {
			log.Error(err)
			return err
		} else {
			b := filepath.Base(dirPath)
			giatrds.FRecords = append(giatrds.FRecords, &pb.FreezedRecord{
				BaseName:    b,
				RemoteURL:   rURL,
				LastUpdated: timestamppb.Now()})
			if data, err := proto.Marshal(&giatrds); err != nil {
				log.Error(err)
				return err
			} else {
				if err := os.WriteFile(GiatRecordPath, data, 0644); err != nil {
					log.Error(err)
					return err
				}
			}
		}
	}
	return nil
}

func FreezedGiatRecords() ([]string, error) {
	zgrds := []string{}
	if data, err := os.ReadFile(GiatRecordPath); err != nil {
		log.Error(err)
		return zgrds, err
	} else {
		giatrds := pb.GiatRecords{}
		if err := proto.Unmarshal(data, &giatrds); err != nil {
			log.Error(err)
			return zgrds, err
		}
		for _, grd := range giatrds.FRecords {
			zgrds = append(zgrds, grd.BaseName+grd.RemoteURL)
		}
	}
	return zgrds, nil
}

func ArrayContainsElemenet[T comparable](s []T, e T) bool {
	for _, v := range s {
		if v == e {
			return true
		}
	}
	return false
}
