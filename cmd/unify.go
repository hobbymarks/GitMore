/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"path/filepath"
	"regexp"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"gopkg.in/ini.v1"
)

// unifyCmd represents the unify command
var unifyCmd = &cobra.Command{
	Use:   "unify",
	Short: "unify git directory name",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		dirs, err := AllGitDirs(args)
		if err != nil {
			log.Error(err)
			return
		}
		for _, gdir := range dirs {
			gr, err := DecodeGitConfig(filepath.Join(gdir, ".git/config"))
			if err != nil {
				log.Error(err)
			} else {
				fmt.Printf("%s-->%s\n", gdir, gr)
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(unifyCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// unifyCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// unifyCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

func DecodeGitConfig(configPath string) (string, error) {
	cfg, err := ini.Load(configPath)
	if err != nil {
		return "", err
	}

	// pattern := regexp.MustCompile(`(github.com/(?P<org>\S+)/(?P<repo>\S+).git)|(github.com/(?P<org>\S+)/(?P<repo>\S+))`)
	pattern := regexp.MustCompile(`(//(\S+)/(?P<org>\S+)/(?P<repo>\S+).git)|(//(\S+)/(?P<org>\S+)/(?P<repo>\S+))`)
	template := []byte("$repo@$org")
	result := []byte{}

	content := []byte(cfg.Section(`remote "origin"`).Key("url").String())
	for _, submatches := range pattern.FindAllSubmatchIndex(content, -1) {
		result = pattern.Expand(result, template, content, submatches)
	}
	log.Trace(string(result))

	return string(result), nil
}
